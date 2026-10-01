import simpy
import sys
import os
import pandas as pd

DISRUPTION_FILE = "data/sample/mobile/disruptions.csv"

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

disruptions = load_disruptions()

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

def run_scheduled_operation(
    env,
    machines,
    job_id,
    operation_id,
    machine_id,
    scheduled_start,
    duration,
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