import simpy
import sys
import os
import pandas as pd

DISRUPTION_FILE = "data/sample/mobile/disruptions.csv"
MAINTENANCE_FILE = "data/sample/mobile/maintenance.csv"

# Add backend/app and scheduler to Python path
APP_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)
SCHEDULER_DIR = os.path.join(APP_DIR, "scheduler")

sys.path.insert(0, APP_DIR)
sys.path.insert(0, SCHEDULER_DIR)

from scheduler.cp_sat_scheduler import create_schedule

def load_disruptions():
    disruptions = pd.read_csv(DISRUPTION_FILE)

    print("\n========== DISRUPTIONS ==========")

    for _, disruption in disruptions.iterrows():
        print(
            f"{disruption['machine_id']} "
            f"unavailable from "
            f"{disruption['start_time']} "
            f"to "
            f"{disruption['end_time']}"
        )

    return disruptions

def load_maintenance():
    maintenance = pd.read_csv(MAINTENANCE_FILE)

    print("\n========== MAINTENANCE ==========")

    for _, row in maintenance.iterrows():
        print(
            f"{row['machine_id']} "
            f"maintenance from "
            f"{row['start_time']} "
            f"to "
            f"{row['end_time']}"
        )

    return maintenance

disruptions = load_disruptions()

maintenance = load_maintenance()

simulation_results = {
    "operations": [],
    "machine_busy_time": {},
}

def create_environment():
    """
    Create and return a SimPy simulation environment.
    """

    env = simpy.Environment()

    return env


def create_machines(env):
    """
    Create SimPy resources for all factory machines.
    """

    machines = {
        "M1": simpy.Resource(env, capacity=1),
        "M2": simpy.Resource(env, capacity=1),
        "M3": simpy.Resource(env, capacity=1),
        "M4": simpy.Resource(env, capacity=1),
        "M5": simpy.Resource(env, capacity=1),
    }

    return machines

def process_operation(env, machines, job_id, operation_id, machine_id, duration):
    """
    Simulate one manufacturing operation.
    """

    machine = machines[machine_id]

    print(
        f"Time {env.now}: "
        f"{job_id}/{operation_id} waiting for {machine_id}"
    )

    with machine.request() as request:

        yield request

        print(
            f"Time {env.now}: "
            f"{job_id}/{operation_id} started on {machine_id}"
        )

        yield env.timeout(duration)

        print(
            f"Time {env.now}: "
            f"{job_id}/{operation_id} finished on {machine_id}"
        ) 

def get_machine_disruption(machine_id, current_time, duration, disruptions):

    for _, disruption in disruptions.iterrows():

        if disruption["machine_id"] != machine_id:
            continue

        disruption_start = disruption["start_time"]
        disruption_end = disruption["end_time"]

        operation_end = current_time + duration

        if (
            current_time < disruption_end
            and operation_end > disruption_start
        ):
            return disruption_start, disruption_end

    return None

def get_next_available_time(
    current_time,
    machine_id,
    processing_time,
    maintenance,
    disruptions
):
    """
    Find the earliest time when the operation can run completely
    without overlapping maintenance or disruption windows.
    """

    start_time = current_time

    while True:
        end_time = start_time + processing_time

        conflict_found = False

        # Check maintenance
        for _, row in maintenance.iterrows():
            if row["machine_id"] == machine_id:
                maintenance_start = row["start_time"]
                maintenance_end = row["end_time"]

                if start_time < maintenance_end and end_time > maintenance_start:
                    start_time = maintenance_end
                    conflict_found = True
                    break

        if conflict_found:
            continue

        # Check disruptions
        for _, row in disruptions.iterrows():
            if row["machine_id"] == machine_id:
                disruption_start = row["start_time"]
                disruption_end = row["end_time"]

                if start_time < disruption_end and end_time > disruption_start:
                    start_time = disruption_end
                    conflict_found = True
                    break

        if not conflict_found:
            return start_time
    
def run_scheduled_operation(
    env,
    machines,
    job_id,
    operation_id,
    machine_id,
    scheduled_start,
    duration,
    maintenance,
    disruptions
):
    # Wait until the scheduled start time
    if env.now < scheduled_start:
        yield env.timeout(scheduled_start - env.now)

    machine = machines[machine_id]

    print(
        f"Time {env.now}: "
        f"{job_id}/{operation_id} waiting for {machine_id}"
    )

    # Request machine
    request_time = env.now

    available_time = get_next_available_time(
    env.now,
    machine_id,
    duration,
    maintenance,
    disruptions
    )

    if available_time > env.now:
        print(
            f"Time {env.now}: {job_id}/{operation_id} "
            f"delayed until {available_time} because {machine_id} is unavailable"
        )

        yield env.timeout(available_time - env.now)

    with machine.request() as request:
        yield request

        actual_start = env.now

        print(
            f"Time {actual_start}: "
            f"{job_id}/{operation_id} started on {machine_id}"
        )

        # Execute operation
        yield env.timeout(duration)

        actual_end = env.now

        print(
            f"Time {actual_end}: "
            f"{job_id}/{operation_id} finished on {machine_id}"
        )

    # Calculate waiting time
    waiting_time = actual_start - request_time

    # Store operation result
    simulation_results["operations"].append({
        "job_id": job_id,
        "operation_id": operation_id,
        "machine_id": machine_id,
        "scheduled_start": scheduled_start,
        "actual_start": actual_start,
        "actual_end": actual_end,
        "processing_time": duration,
        "waiting_time": waiting_time
    })

    # Add machine busy time
    if machine_id not in simulation_results["machine_busy_time"]:
        simulation_results["machine_busy_time"][machine_id] = 0

    simulation_results["machine_busy_time"][machine_id] += duration

def simulate_schedule(env, machines, schedule):
    """
    Simulate all operations from the CP-SAT schedule.
    """

    for operation in schedule:
        env.process(
            run_scheduled_operation(
                env,
                machines,
                operation["job_id"],
                operation["operation_id"],
                operation["machine_id"],
                operation["start"],
                operation["processing_time"],
                maintenance,
                disruptions
            )
        )
    
def calculate_simulation_results():
    operations = simulation_results["operations"]

    if not operations:
        print("❌ No simulation results available.")
        return

    # Total operations
    total_operations = len(operations)

    # Completed operations
    completed_operations = sum(
        1 for op in operations
        if op["actual_end"] is not None
    )

    # Simulation makespan
    simulation_makespan = max(
        op["actual_end"] for op in operations
    )

    # Total processing time
    total_processing_time = sum(
        op["processing_time"] for op in operations
    )

    # Total waiting time
    total_waiting_time = sum(
        op["waiting_time"] for op in operations
    )

    print("\n========== SIMULATION RESULTS ==========")

    print(f"Total Operations     : {total_operations}")
    print(f"Completed Operations : {completed_operations}")
    print(f"Simulation Makespan  : {simulation_makespan}")
    print(f"Total Processing Time: {total_processing_time}")
    print(f"Total Waiting Time   : {total_waiting_time}")

    # ==========================================
    # CP-SAT vs SIMULATION VALIDATION
    # ==========================================

    cp_sat_makespan = max(
        operation["end"]
        for operation in schedule
    )

    print("\n========== CP-SAT vs SIMULATION ==========")

    print(f"CP-SAT Makespan       : {cp_sat_makespan}")
    print(f"Simulation Makespan   : {simulation_makespan}")
    print(f"Makespan Difference   : {simulation_makespan - cp_sat_makespan}")

    print(f"Planned Operations    : {len(schedule)}")
    print(f"Completed Operations  : {completed_operations}")

    if simulation_makespan == cp_sat_makespan:
        print("✓ Makespan matches")
    else:
        print("✗ Makespan mismatch")

    if len(schedule) == completed_operations:
        print("✓ All operations completed")
    else:
        print("✗ Operation count mismatch")

    if (
        simulation_makespan == cp_sat_makespan
        and len(schedule) == completed_operations
    ):
        print("\n✅ CP-SAT AND SIMULATION CONSISTENT")
    else:
        print("\n⚠️ CP-SAT AND SIMULATION DIFFER")
        # Machine utilization
        print("\nMachine Utilization:")

        for machine_id, busy_time in sorted(
            simulation_results["machine_busy_time"].items()
        ):
            utilization = (
                busy_time / simulation_makespan
            ) * 100

            print(
                f"{machine_id} : "
                f"{utilization:.2f}% "
                f"(Busy: {busy_time})"
            )

    # Job completion times
    print("\nJob Completion Times:")

    job_completion = {}

    for operation in operations:
        job_id = operation["job_id"]
        end_time = operation["actual_end"]

        if (
            job_id not in job_completion
            or end_time > job_completion[job_id]
        ):
            job_completion[job_id] = end_time

    for job_id, completion_time in sorted(job_completion.items()):
        print(
            f"{job_id} : "
            f"{completion_time}"
        )

if __name__ == "__main__":

    # Create SimPy environment
    env = create_environment()

    # Create factory machines
    machines = create_machines(env)

    print("SimPy environment created successfully.")
    print("Current simulation time:", env.now)

    print("\nMachines created:")

    for machine_id in machines:
        print(
            f"{machine_id} -> "
            f"capacity: {machines[machine_id].capacity}"
        )

    # =========================================================
    # GET OPTIMIZED SCHEDULE FROM CP-SAT
    # =========================================================

    print("\n========== GETTING CP-SAT SCHEDULE ==========")

    schedule = create_schedule()

    if schedule is None:
        print("❌ No schedule available.")
        exit()

    print(
        f"\nReceived {len(schedule)} operations from CP-SAT."
    )

    # =========================================================
    # SIMULATE SCHEDULE
    # =========================================================

    print("\n========== SIMULATION ==========")

    simulate_schedule(
        env,
        machines,
        schedule
    )

    # Run simulation
    env.run()

    print("\nSimulation completed.")

    calculate_simulation_results()