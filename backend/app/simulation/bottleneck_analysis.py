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
# CALCULATE MACHINE METRICS
# =============================================================

def calculate_machine_metrics(schedule):

    if not schedule:
        print("❌ No schedule available.")
        return None

    # ---------------------------------------------------------
    # Makespan
    # ---------------------------------------------------------

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    # ---------------------------------------------------------
    # Calculate busy time for every machine
    # ---------------------------------------------------------

    machine_busy_time = {}

    for operation in schedule:

        machine_id = operation["machine_id"]

        processing_time = (
            operation["end"]
            - operation["start"]
        )

        machine_busy_time[machine_id] = (
            machine_busy_time.get(machine_id, 0)
            + processing_time
        )

    # ---------------------------------------------------------
    # Calculate idle time and utilization
    # ---------------------------------------------------------

    machine_metrics = {}

    for machine_id, busy_time in sorted(
        machine_busy_time.items()
    ):

        idle_time = makespan - busy_time

        utilization = (
            busy_time / makespan
        ) * 100

        machine_metrics[machine_id] = {
            "busy_time": busy_time,
            "idle_time": idle_time,
            "utilization": utilization
        }

    return makespan, machine_metrics


# =============================================================
# BOTTLENECK ANALYSIS
# =============================================================

def analyze_bottleneck(machine_metrics):

    # Machine with highest utilization
    bottleneck_machine = max(
        machine_metrics,
        key=lambda machine:
            machine_metrics[machine]["utilization"]
    )

    bottleneck_utilization = machine_metrics[
        bottleneck_machine
    ]["utilization"]

    return (
        bottleneck_machine,
        bottleneck_utilization
    )


# =============================================================
# PRINT MACHINE ANALYSIS
# =============================================================

def print_machine_analysis(
    makespan,
    machine_metrics
):

    print("\n========== MACHINE ANALYSIS ==========")

    print(f"Makespan : {makespan}")

    print("\nMachine Metrics:")

    for machine_id, metrics in machine_metrics.items():

        print(
            f"{machine_id} | "
            f"Busy: {metrics['busy_time']} | "
            f"Idle: {metrics['idle_time']} | "
            f"Utilization: "
            f"{metrics['utilization']:.2f}%"
        )


# =============================================================
# PRINT BOTTLENECK
# =============================================================

def print_bottleneck(
    bottleneck_machine,
    bottleneck_utilization
):

    print("\n========== BOTTLENECK ANALYSIS ==========")

    print(
        f"Highest Utilized Machine : "
        f"{bottleneck_machine}"
    )

    print(
        f"Utilization              : "
        f"{bottleneck_utilization:.2f}%"
    )



def plot_machine_idle_time(machine_metrics):

    fig, ax = plt.subplots(figsize=(12, 8))

    machines = list(machine_metrics.keys())
    idle_times = [
        machine_metrics[m]["idle_time"]
        for m in machines
    ]

    bars = ax.bar(machines, idle_times)

    ax.set_title(
        "Smart Job Shop Optimizer - Machine Idle Time"
    )

    ax.set_xlabel("Machine")
    ax.set_ylabel("Idle Time")

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    for bar, value in zip(bars, idle_times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.3,
            str(value),
            ha="center"
        )

    return fig


def plot_machine_time_distribution(machine_metrics):

    fig, ax = plt.subplots(figsize=(12, 8))

    machines = list(machine_metrics.keys())

    busy_times = [
        machine_metrics[m]["busy_time"]
        for m in machines
    ]

    idle_times = [
        machine_metrics[m]["idle_time"]
        for m in machines
    ]

    ax.bar(
        machines,
        busy_times,
        label="Busy"
    )

    ax.bar(
        machines,
        idle_times,
        bottom=busy_times,
        label="Idle"
    )

    ax.set_title(
        "Smart Job Shop Optimizer - Machine Time Distribution"
    )

    ax.set_xlabel("Machine")
    ax.set_ylabel("Time")

    ax.legend()

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    return fig


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    print(
        "\n========== GETTING CP-SAT SCHEDULE =========="
    )

    schedule = create_schedule()

    if not schedule:

        print("❌ CP-SAT did not return a schedule.")

    else:

        result = calculate_machine_metrics(
            schedule
        )

        if result is None:

            print("❌ Could not calculate machine metrics.")

        else:

            makespan, machine_metrics = result

            print_machine_analysis(
                makespan,
                machine_metrics
            )

            (
                bottleneck_machine,
                bottleneck_utilization
            ) = analyze_bottleneck(
                machine_metrics
            )

            print_bottleneck(
                bottleneck_machine,
                bottleneck_utilization
            )

            print(
                "\n========== VISUALIZATION =========="
            )

            plot_machine_idle_time(machine_metrics)

            plot_machine_time_distribution(machine_metrics)

            plt.show()
    
            print(
                "\n✅ BOTTLENECK ANALYSIS COMPLETED"
            )