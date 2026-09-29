import simpy
import sys
import os

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
def run_scheduled_operation(env,machines,job_id,operation_id,machine_id,scheduled_start,duration):
    """
    Execute one operation according to the CP-SAT schedule.
    """

    # Wait until the scheduled start time
    if env.now < scheduled_start:
        yield env.timeout(scheduled_start - env.now)

    machine = machines[machine_id]

    print(
        f"Time {env.now}: "
        f"{job_id}/{operation_id} waiting for {machine_id}"
    )

    with machine.request() as request:

        yield request

        actual_start = env.now

        print(
            f"Time {actual_start}: "
            f"{job_id}/{operation_id} started on {machine_id}"
        )

        yield env.timeout(duration)

        actual_end = env.now

        print(
            f"Time {actual_end}: "
            f"{job_id}/{operation_id} finished on {machine_id}"
        ) 
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
                operation["processing_time"]
            )
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