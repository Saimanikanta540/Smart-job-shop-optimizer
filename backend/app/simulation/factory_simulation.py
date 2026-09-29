import simpy


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


if __name__ == "__main__":

    env = create_environment()

    machines = create_machines(env)

    print("SimPy environment created successfully.")
    print("Current simulation time:", env.now)

    print("\nMachines created:")

    for machine_id in machines:
        print(
            f"{machine_id} -> "
            f"capacity: {machines[machine_id].capacity}"
        )