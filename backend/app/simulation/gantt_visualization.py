import sys
from pathlib import Path

import matplotlib.pyplot as plt

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scheduler.cp_sat_scheduler import create_schedule
from backend.app.scheduler.data_loader import load_data

def plot_gantt(schedule):
    """
    Plot the CP-SAT optimized schedule as a Gantt chart.
    """

    if not schedule:
        print("❌ No schedule available for visualization.")
        return

    # Get unique machines
    machines = sorted(
        set(operation["machine_id"] for operation in schedule)
    )

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot each operation
    for operation in schedule:

        job_id = operation["job_id"]
        operation_id = operation["operation_id"]
        machine_id = operation["machine_id"]

        start = operation["start"]
        end = operation["end"]

        duration = end - start

        machine_index = machines.index(machine_id)

        # Operation block
        ax.barh(
            machine_index,
            duration,
            left=start,
            height=0.6
        )

        # Operation label
        ax.text(
            start + duration / 2,
            machine_index,
            f"{job_id}/{operation_id}",
            ha="center",
            va="center",
            fontsize=9
        )

    # -----------------------------
    # Y-axis
    # -----------------------------

    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machines)

    # M1 at top
    ax.invert_yaxis()

    # -----------------------------
    # Makespan
    # -----------------------------

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    ax.set_xlim(0, makespan + 2)

    # -----------------------------
    # Labels
    # -----------------------------

    ax.set_xlabel("Time")
    ax.set_ylabel("Machine")

    ax.set_title(
        "Smart Job Shop Optimizer - CP-SAT Gantt Chart\n"
        f"Makespan: {makespan}"
    )

    # -----------------------------
    # Grid
    # -----------------------------

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    print("\n========== GANTT VISUALIZATION ==========")
    print(f"Operations : {len(schedule)}")
    print(f"Makespan   : {makespan}")
    print("Gantt chart generated successfully.")

    plt.show()


if __name__ == "__main__":

    print("\n========== GETTING CP-SAT SCHEDULE ==========")

    schedule = create_schedule()

    if schedule:
        plot_gantt(schedule)
    else:
        print("❌ CP-SAT did not return a schedule.")