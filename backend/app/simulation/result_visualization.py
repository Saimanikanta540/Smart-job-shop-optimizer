import sys
from pathlib import Path

import matplotlib.pyplot as plt

# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scheduler.cp_sat_scheduler import create_schedule


# =============================================================
# GET SCHEDULE DATA
# =============================================================

def get_result_data(schedule):
    """
    Calculate result metrics required for visualization.
    """

    if not schedule:
        return None

    # ---------------------------------------------------------
    # Makespan
    # ---------------------------------------------------------

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    # ---------------------------------------------------------
    # Machine utilization
    # ---------------------------------------------------------

    machine_busy_time = {}

    for operation in schedule:

        machine_id = operation["machine_id"]
        processing_time = (
            operation["end"] - operation["start"]
        )

        machine_busy_time[machine_id] = (
            machine_busy_time.get(machine_id, 0)
            + processing_time
        )

    machine_utilization = {}

    for machine_id, busy_time in machine_busy_time.items():

        utilization = (
            busy_time / makespan
        ) * 100

        machine_utilization[machine_id] = utilization

    # ---------------------------------------------------------
    # Job completion times
    # ---------------------------------------------------------

    job_completion = {}

    for operation in schedule:

        job_id = operation["job_id"]
        end_time = operation["end"]

        if (
            job_id not in job_completion
            or end_time > job_completion[job_id]
        ):
            job_completion[job_id] = end_time

    return {
        "total_operations": len(schedule),
        "makespan": makespan,
        "machine_utilization": machine_utilization,
        "job_completion": job_completion
    }


# =============================================================
# MACHINE UTILIZATION VISUALIZATION
# =============================================================

def plot_machine_utilization(machine_utilization):

    machines = list(machine_utilization.keys())
    utilization = list(machine_utilization.values())

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        machines,
        utilization
    )

    plt.xlabel("Machine")
    plt.ylabel("Utilization (%)")

    plt.title(
        "Smart Job Shop Optimizer - Machine Utilization"
    )

    plt.ylim(0, 100)

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    # Display percentage on top of bars
    for bar, value in zip(bars, utilization):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.2f}%",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.show()


# =============================================================
# JOB COMPLETION VISUALIZATION
# =============================================================

def plot_job_completion(job_completion):

    jobs = list(job_completion.keys())
    completion_times = list(job_completion.values())

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        jobs,
        completion_times
    )

    plt.xlabel("Job")
    plt.ylabel("Completion Time")

    plt.title(
        "Smart Job Shop Optimizer - Job Completion Times"
    )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    # Display completion time
    for bar, value in zip(
        bars,
        completion_times
    ):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(value),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.show()


# =============================================================
# OVERALL SUMMARY VISUALIZATION
# =============================================================

def plot_summary(total_operations, makespan):

    labels = [
        "Operations",
        "Makespan"
    ]

    values = [
        total_operations,
        makespan
    ]

    plt.figure(figsize=(8, 6))

    bars = plt.bar(
        labels,
        values
    )

    plt.ylabel("Value")

    plt.title(
        "Smart Job Shop Optimizer - Overall Results"
    )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    for bar, value in zip(bars, values):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(value),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.show()


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    print("\n========== GETTING CP-SAT SCHEDULE ==========")

    schedule = create_schedule()

    if not schedule:

        print("❌ CP-SAT did not return a schedule.")

    else:

        results = get_result_data(schedule)

        print("\n========== RESULT VISUALIZATION ==========")

        print(
            f"Operations : "
            f"{results['total_operations']}"
        )

        print(
            f"Makespan   : "
            f"{results['makespan']}"
        )

        print("\nMachine Utilization:")

        for machine, utilization in sorted(
            results["machine_utilization"].items()
        ):

            print(
                f"{machine} : "
                f"{utilization:.2f}%"
            )

        print("\nJob Completion:")

        for job, completion in sorted(
            results["job_completion"].items()
        ):

            print(
                f"{job} : "
                f"{completion}"
            )

        # -----------------------------------------------------
        # Visualizations
        # -----------------------------------------------------

        plot_machine_utilization(
            results["machine_utilization"]
        )

        plot_job_completion(
            results["job_completion"]
        )

        plot_summary(
            results["total_operations"],
            results["makespan"]
        )

        print(
            "\n✅ RESULT VISUALIZATION COMPLETED"
        )