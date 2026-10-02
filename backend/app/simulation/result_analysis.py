import sys
from pathlib import Path

# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scheduler.cp_sat_scheduler import create_schedule

def analyze_schedule(schedule):
    """
    Analyze the CP-SAT optimized schedule.

    Calculates:
    - Makespan
    - Total operations
    - Machine utilization
    - Job completion times
    - Machine busy time
    """

    if not schedule:
        print("❌ No schedule available for analysis.")
        return

    # ============================================================
    # BASIC INFORMATION
    # ============================================================

    total_operations = len(schedule)

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    print("\n========== RESULT ANALYSIS ==========")

    print(f"Total Operations : {total_operations}")
    print(f"Makespan         : {makespan}")

    # ============================================================
    # MACHINE BUSY TIME
    # ============================================================

    machine_busy_time = {}

    for operation in schedule:

        machine_id = operation["machine_id"]

        duration = (
            operation["end"]
            - operation["start"]
        )

        machine_busy_time[machine_id] = (
            machine_busy_time.get(machine_id, 0)
            + duration
        )

    # ============================================================
    # MACHINE UTILIZATION
    # ============================================================

    print("\n========== MACHINE UTILIZATION ==========")

    for machine_id, busy_time in sorted(
        machine_busy_time.items()
    ):

        utilization = (
            busy_time / makespan
        ) * 100

        print(
            f"{machine_id} : "
            f"{utilization:.2f}% "
            f"(Busy: {busy_time})"
        )

    # ============================================================
    # JOB COMPLETION TIMES
    # ============================================================

    print("\n========== JOB COMPLETION TIMES ==========")

    job_completion = {}

    for operation in schedule:

        job_id = operation["job_id"]
        end_time = operation["end"]

        if (
            job_id not in job_completion
            or end_time > job_completion[job_id]
        ):
            job_completion[job_id] = end_time

    for job_id, completion_time in sorted(
        job_completion.items()
    ):

        print(
            f"{job_id} : "
            f"{completion_time}"
        )

    # ============================================================
    # MACHINE SUMMARY
    # ============================================================

    print("\n========== MACHINE SUMMARY ==========")

    for machine_id in sorted(machine_busy_time):

        busy_time = machine_busy_time[machine_id]

        idle_time = makespan - busy_time

        utilization = (
            busy_time / makespan
        ) * 100

        print(
            f"{machine_id} | "
            f"Busy: {busy_time} | "
            f"Idle: {idle_time} | "
            f"Utilization: {utilization:.2f}%"
        )

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print("\n========== FINAL SUMMARY ==========")

    print(f"Operations : {total_operations}")
    print(f"Makespan   : {makespan}")

    print("\nJob Completion:")

    for job_id, completion_time in sorted(
        job_completion.items()
    ):
        print(
            f"  {job_id} -> {completion_time}"
        )

    print("\nMachine Utilization:")

    for machine_id in sorted(machine_busy_time):

        utilization = (
            machine_busy_time[machine_id]
            / makespan
        ) * 100

        print(
            f"  {machine_id} -> "
            f"{utilization:.2f}%"
        )

    print("\n✅ RESULT ANALYSIS COMPLETED")


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    print("\n========== GETTING CP-SAT SCHEDULE ==========")

    schedule = create_schedule()

    if schedule:
        analyze_schedule(schedule)
    else:
        print("❌ CP-SAT did not return a schedule.")