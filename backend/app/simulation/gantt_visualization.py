import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scheduler.cp_sat_scheduler import create_schedule


# =============================================================
# GANTT VISUALIZATION
# =============================================================

def plot_gantt(schedule):
    """
    Plot the CP-SAT optimized schedule as a Gantt chart.

    Features:
    - Same color for the same job
    - Maintenance periods
    - Machine disruption periods
    - Operation labels
    - Makespan
    """

    if not schedule:
        print("❌ No schedule available for visualization.")
        return

    # =========================================================
    # MACHINE INFORMATION
    # =========================================================

    machines = sorted(
        set(operation["machine_id"] for operation in schedule)
    )

    # =========================================================
    # JOB COLORS
    # =========================================================

    jobs = sorted(
        set(operation["job_id"] for operation in schedule)
    )

    cmap = plt.get_cmap("tab10")

    job_colors = {
        job_id: cmap(index % 10)
        for index, job_id in enumerate(jobs)
    }

    # =========================================================
    # CREATE FIGURE
    # =========================================================

    fig, ax = plt.subplots(figsize=(16, 8))

    # =========================================================
    # PLOT OPERATIONS
    # =========================================================

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
            height=0.6,
            color=job_colors[job_id],
            edgecolor="black"
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

    # =========================================================
    # MAINTENANCE WINDOWS
    # =========================================================

    maintenance = [
        {
            "machine_id": "M1",
            "start": 10,
            "end": 15
        }
    ]

    for item in maintenance:

        machine_id = item["machine_id"]
        start = item["start"]
        end = item["end"]

        if machine_id not in machines:
            continue

        machine_index = machines.index(machine_id)

        ax.barh(
            machine_index,
            end - start,
            left=start,
            height=0.85,
            color="gray",
            alpha=0.35,
            hatch="//",
            edgecolor="black"
        )

        ax.text(
            (start + end) / 2,
            machine_index,
            "MAINTENANCE",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold"
        )

    # =========================================================
    # MACHINE DISRUPTIONS
    # =========================================================

    disruptions = [
        {
            "machine_id": "M2",
            "start": 12,
            "end": 18
        },
        {
            "machine_id": "M3",
            "start": 18,
            "end": 20
        }
    ]

    for item in disruptions:

        machine_id = item["machine_id"]
        start = item["start"]
        end = item["end"]

        if machine_id not in machines:
            continue

        machine_index = machines.index(machine_id)

        ax.barh(
            machine_index,
            end - start,
            left=start,
            height=0.85,
            color="red",
            alpha=0.20,
            hatch="xx",
            edgecolor="red"
        )

        ax.text(
            (start + end) / 2,
            machine_index,
            "DISRUPTION",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold"
        )

    # =========================================================
    # Y-AXIS
    # =========================================================

    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machines)

    # M1 at top
    ax.invert_yaxis()

    # =========================================================
    # MAKESPAN
    # =========================================================

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    ax.set_xlim(0, makespan + 2)

    # =========================================================
    # LABELS
    # =========================================================

    ax.set_xlabel("Time")
    ax.set_ylabel("Machine")

    ax.set_title(
        "Smart Job Shop Optimizer - CP-SAT Gantt Chart\n"
        f"Makespan: {makespan}"
    )

    # =========================================================
    # GRID
    # =========================================================

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=0.5
    )

    # =========================================================
    # LEGEND
    # =========================================================

    job_legend = [
        Patch(
            facecolor=job_colors[job],
            edgecolor="black",
            label=job
        )
        for job in jobs
    ]

    maintenance_legend = Patch(
        facecolor="gray",
        edgecolor="black",
        hatch="//",
        alpha=0.35,
        label="Maintenance"
    )

    disruption_legend = Patch(
        facecolor="red",
        edgecolor="red",
        hatch="xx",
        alpha=0.20,
        label="Disruption"
    )

    ax.legend(
        handles=job_legend + [
            maintenance_legend,
            disruption_legend
        ],
        title="Legend",
        loc="upper right"
    )

    # =========================================================
    # FINALIZE
    # =========================================================

    plt.tight_layout()

    print("\n========== GANTT VISUALIZATION ==========")
    print(f"Operations : {len(schedule)}")
    print(f"Makespan   : {makespan}")
    print("Job colors : Consistent")
    print("Maintenance: Displayed")
    print("Disruptions: Displayed")
    print("Gantt chart generated successfully.")

    plt.show()


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    print("\n========== GETTING CP-SAT SCHEDULE ==========")

    schedule = create_schedule()

    if schedule:
        plot_gantt(schedule)
    else:
        print("❌ CP-SAT did not return a schedule.")