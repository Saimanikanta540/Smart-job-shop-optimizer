import simpy


def create_environment():
    """
    Create and return a SimPy simulation environment.
    """

    env = simpy.Environment()

    return env


if __name__ == "__main__":

    env = create_environment()

    print("SimPy environment created successfully.")
    print("Current simulation time:", env.now)