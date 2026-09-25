from ortools.sat.python import cp_model

from data_loader import load_data


def create_schedule():
    # ---------------------------------------------------------
    # 1. Load factory data
    # ---------------------------------------------------------
    machines, jobs, operations = load_data()

    # ---------------------------------------------------------
    # 2. Create CP-SAT model
    # ---------------------------------------------------------
    model = cp_model.CpModel()

    # A sufficiently large time horizon.
    # We will improve this later.
    horizon = sum(operations["processing_time"])

    # ---------------------------------------------------------
    # 3. Dictionaries to store OR-Tools variables
    # ---------------------------------------------------------
    start_vars = {}
    end_vars = {}
    interval_vars = {}

    # ---------------------------------------------------------
    # 4. Create variables for every operation
    # ---------------------------------------------------------
    for _, operation in operations.iterrows():

        operation_id = operation["operation_id"]
        duration = int(operation["processing_time"])

        start = model.NewIntVar(
            0,
            horizon,
            f"start_{operation_id}"
        )

        end = model.NewIntVar(
            0,
            horizon,
            f"end_{operation_id}"
        )

        interval = model.NewIntervalVar(
            start,
            duration,
            end,
            f"interval_{operation_id}"
        )

        start_vars[operation_id] = start
        end_vars[operation_id] = end
        interval_vars[operation_id] = interval

    # ---------------------------------------------------------
    # 5. Add operation precedence constraints
    # ---------------------------------------------------------
    for job_id in operations["job_id"].unique():

        job_operations = operations[
            operations["job_id"] == job_id
        ].sort_values("sequence")

        operation_ids = job_operations[
            "operation_id"
        ].tolist()

        for i in range(len(operation_ids) - 1):

            current_operation = operation_ids[i]
            next_operation = operation_ids[i + 1]

            model.Add(
                start_vars[next_operation]
                >= end_vars[current_operation]
            )

    # ---------------------------------------------------------
    # 6. Add machine no-overlap constraints
    # ---------------------------------------------------------
    for machine_id in operations["machine_id"].unique():

        machine_operations = operations[
            operations["machine_id"] == machine_id
        ]

        machine_intervals = []

        for _, operation in machine_operations.iterrows():

            operation_id = operation["operation_id"]

            machine_intervals.append(
                interval_vars[operation_id]
            )

        model.AddNoOverlap(machine_intervals)

    # ---------------------------------------------------------
    # 7. Create makespan variable
    # ---------------------------------------------------------
    makespan = model.NewIntVar(
        0,
        horizon,
        "makespan"
    )

    # Every operation must finish before makespan.
    for operation_id in end_vars:

        model.Add(
            makespan >= end_vars[operation_id]
        )

    # ---------------------------------------------------------
    # 8. Objective: minimize makespan
    # ---------------------------------------------------------
    model.Minimize(makespan)

    # ---------------------------------------------------------
    # 9. Solve model
    # ---------------------------------------------------------
    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    # ---------------------------------------------------------
    # 10. Check result
    # ---------------------------------------------------------
    if status in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        print("\n========== OPTIMIZED SCHEDULE ==========\n")

        for _, operation in operations.iterrows():

            operation_id = operation["operation_id"]

            print(
                f"{operation['job_id']} | "
                f"{operation_id} | "
                f"{operation['machine_id']} | "
                f"Start: {solver.Value(start_vars[operation_id])} | "
                f"End: {solver.Value(end_vars[operation_id])}"
            )

        print(
            f"\nMakespan: {solver.Value(makespan)}"
        )

    else:

        print("No feasible schedule found.")


if __name__ == "__main__":
    create_schedule()