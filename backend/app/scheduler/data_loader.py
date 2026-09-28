import pandas as pd


DATA_PATH = "data/sample/mobile"

def load_data():
    machines = pd.read_csv(f"{DATA_PATH}/machines.csv")
    jobs = pd.read_csv(f"{DATA_PATH}/jobs.csv")
    operations = pd.read_csv(f"{DATA_PATH}/operations.csv")
    maintenance = pd.read_csv(f"{DATA_PATH}/maintenance.csv")

    return machines, jobs, operations, maintenance


if __name__ == "__main__":
    machines, jobs, operations, maintenance = load_data()

    print("\nMachines:")
    print(machines)

    print("\nJobs:")
    print(jobs)

    print("\nOperations:")
    print(operations)

    print("\nMaintenance:")
    print(maintenance)