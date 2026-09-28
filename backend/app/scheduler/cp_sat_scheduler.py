from ortools.sat.python import cp_model

from data_loader import load_data

# =========================================================
# FACTORY CALENDAR
# =========================================================

WORKING_WINDOWS = [
    (0, 300),      # 08:00 - 13:00
    (360, 540)     # 14:00 - 17:00
]

def create_schedule():

    # =========================================================
    # 1. LOAD DATA
    # =========================================================

    machines, jobs, operations = load_data()

    print("\n========== INPUT DATA ==========")
    print(f"Jobs       : {len(jobs)}")
    print(f"Machines   : {len(machines)}")
    print(f"Operations : {len(operations)}")


    # =========================================================
    # 2. CREATE CP-SAT MODEL
    # =========================================================

    model = cp_model.CpModel()


   # =========================================================
    # 3. CALCULATE TIME HORIZON
    # =========================================================

    horizon = 540

    print(f"Time Horizon: {horizon}")


    # =========================================================
    # 4. CREATE VARIABLE DICTIONARIES
    # =========================================================

    start_vars = {}
    end_vars = {}
    interval_vars = {}

    # =========================================================
    # 5. CREATE VARIABLES FOR EVERY OPERATION
    # =========================================================

    for _, operation in operations.iterrows():

        operation_id = operation["operation_id"]

        duration = int(
            operation["processing_time"]
        )

        # -----------------------------------------------------
        # Main start/end variables
        # -----------------------------------------------------

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

        start_vars[operation_id] = start
        end_vars[operation_id] = end


        # -----------------------------------------------------
        # Calendar window alternatives
        # -----------------------------------------------------

        window_intervals = []
        window_presence = []

        for window_index, (window_start, window_end) in enumerate(
            WORKING_WINDOWS
        ):

            # This operation cannot fit in this window.
            if duration > (window_end - window_start):
                continue

            presence = model.NewBoolVar(
                f"{operation_id}_window_{window_index}"
            )

            interval = model.NewOptionalIntervalVar(
                start,
                duration,
                end,
                presence,
                f"{operation_id}_interval_{window_index}"
            )

            # If this window is selected:
            #
            # start >= window_start
            # end <= window_end

            model.Add(
                start >= window_start
            ).OnlyEnforceIf(presence)

            model.Add(
                end <= window_end
            ).OnlyEnforceIf(presence)

            window_intervals.append(interval)
            window_presence.append(presence)


        # -----------------------------------------------------
        # Exactly one working window must be selected
        # -----------------------------------------------------

        model.AddExactlyOne(
            window_presence
        )

        interval_vars[operation_id] = window_intervals

    # =========================================================
    # 6. JOB PRECEDENCE CONSTRAINTS
    # =========================================================

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


    # =========================================================
    # 7. MACHINE NO-OVERLAP CONSTRAINTS
    # =========================================================

    for machine_id in operations["machine_id"].unique():

        machine_operations = operations[
            operations["machine_id"] == machine_id
        ]

        machine_intervals = []

        for _, operation in machine_operations.iterrows():

            operation_id = operation["operation_id"]

            machine_intervals.extend(
                interval_vars[operation_id]
            )

        model.AddNoOverlap(
            machine_intervals
        )


    # =========================================================
    # 8. MAKESPAN
    # =========================================================

    makespan = model.NewIntVar(
        0,
        horizon,
        "makespan"
    )

    for operation_id in end_vars:

        model.Add(
            makespan >= end_vars[operation_id]
        )


    # =========================================================
    # 9. OPTIMIZATION OBJECTIVE
    # =========================================================

    model.Minimize(makespan)


    # =========================================================
    # 10. SOLVE
    # =========================================================

    solver = cp_model.CpSolver()

    status = solver.Solve(model)


    # =========================================================
    # 11. CHECK SOLUTION
    # =========================================================

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        print("\n❌ No feasible schedule found.")

        return None


    # =========================================================
    # 12. EXTRACT SCHEDULE
    # =========================================================

    schedule = []

    for _, operation in operations.iterrows():

        operation_id = operation["operation_id"]

        start = solver.Value(
            start_vars[operation_id]
        )

        end = solver.Value(
            end_vars[operation_id]
        )

        schedule.append({

            "job_id": operation["job_id"],

            "operation_id": operation_id,

            "machine_id": operation["machine_id"],

            "sequence": int(operation["sequence"]),

            "processing_time": int(
                operation["processing_time"]
            ),

            "start": start,

            "end": end
        })


    # =========================================================
    # 13. SORT SCHEDULE
    # =========================================================

    schedule.sort(
        key=lambda x: (
            x["machine_id"],
            x["start"]
        )
    )


    # =========================================================
    # 14. PRINT SCHEDULE
    # =========================================================

    print(
        "\n========== OPTIMIZED SCHEDULE ==========\n"
    )

    for item in schedule:

        print(
            f"{item['job_id']} | "
            f"{item['operation_id']} | "
            f"{item['machine_id']} | "
            f"Start: {item['start']} | "
            f"End: {item['end']}"
        )

    print(
        f"\nMakespan: {solver.Value(makespan)}"
    )


    # =========================================================
    # 15. VALIDATE
    # =========================================================

    validate_schedule(
        schedule,
        solver.Value(makespan)
    )

    return schedule
# =============================================================
# CALENDAR VALIDATION HELPER
# =============================================================

def is_inside_working_window(start, end):

    for window_start, window_end in WORKING_WINDOWS:

        if start >= window_start and end <= window_end:
            return True

    return False

# =============================================================
# VALIDATION FUNCTION
# =============================================================

def validate_schedule(schedule, makespan):

    print(
        "\n========== SCHEDULE VALIDATION ==========\n"
    )

    valid = True


    # =========================================================
    # CHECK 1 — PROCESSING TIME
    # =========================================================

    for operation in schedule:

        expected_end = (
            operation["start"]
            + operation["processing_time"]
        )

        if operation["end"] != expected_end:

            print(
                f"❌ Duration error: "
                f"{operation['operation_id']}"
            )

            valid = False


    if valid:

        print(
            "✓ Processing times are correct"
        )


    # =========================================================
    # CHECK 2 — JOB PRECEDENCE
    # =========================================================

    jobs = {}

    for operation in schedule:

        job_id = operation["job_id"]

        if job_id not in jobs:

            jobs[job_id] = []

        jobs[job_id].append(operation)


    precedence_valid = True

    for job_id, job_operations in jobs.items():

        job_operations.sort(
            key=lambda x: x["sequence"]
        )

        for i in range(
            len(job_operations) - 1
        ):

            current = job_operations[i]
            next_operation = job_operations[i + 1]

            if next_operation["start"] < current["end"]:

                print(
                    f"❌ Precedence error: "
                    f"{job_id} "
                    f"{current['operation_id']} → "
                    f"{next_operation['operation_id']}"
                )

                precedence_valid = False
                valid = False


    if precedence_valid:

        print(
            "✓ Job precedence is valid"
        )


    # =========================================================
    # CHECK 3 — MACHINE OVERLAP
    # =========================================================

    machines = {}

    for operation in schedule:

        machine_id = operation["machine_id"]

        if machine_id not in machines:

            machines[machine_id] = []

        machines[machine_id].append(operation)


    machine_valid = True

    for machine_id, machine_operations in machines.items():

        machine_operations.sort(
            key=lambda x: x["start"]
        )

        for i in range(
            len(machine_operations) - 1
        ):

            current = machine_operations[i]
            next_operation = machine_operations[i + 1]

            if next_operation["start"] < current["end"]:

                print(
                    f"❌ Machine overlap: "
                    f"{machine_id} "
                    f"{current['operation_id']} / "
                    f"{next_operation['operation_id']}"
                )

                machine_valid = False
                valid = False


    if machine_valid:

        print(
            "✓ Machine no-overlap constraint is valid"
        )


    # =========================================================
    # CHECK 4 — MAKESPAN
    # =========================================================

    calculated_makespan = max(
        operation["end"]
        for operation in schedule
    )

    if calculated_makespan == makespan:

        print(
            f"✓ Makespan is correct: {makespan}"
        )

    else:

        print(
            f"❌ Makespan error: "
            f"Expected {calculated_makespan}, "
            f"Got {makespan}"
        )

        valid = False

    # =========================================================
    # CHECK 5 — WORKING HOURS / BREAKS
    # =========================================================

    calendar_valid = True

    for operation in schedule:

        if not is_inside_working_window(
            operation["start"],
            operation["end"]
        ):

            print(
                f"❌ Calendar violation: "
                f"{operation['operation_id']} "
                f"runs from "
                f"{operation['start']} to "
                f"{operation['end']}"
            )

            calendar_valid = False
            valid = False

    if calendar_valid:

        print(
            "✓ Working hours and breaks are respected"
        )

    # =========================================================
    # FINAL RESULT
    # =========================================================

    print()

    if valid:

        print(
            "✅ SCHEDULE VALID"
        )

    else:

        print(
            "❌ SCHEDULE INVALID"
        )
if __name__ == "__main__":
    create_schedule()