import sys
from pathlib import Path

import matplotlib.pyplot as plt

# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.scheduler.cp_sat_scheduler import create_schedule


# ============================================================
# CALCULATE MACHINE METRICS
# ============================================================

def calculate_machine_metrics(schedule):
    """
    Calculate busy time, idle time and utilization
    for every machine.
    """

    if not schedule:
        return {}

    makespan = max(
        operation["end"]
        for operation in schedule
    )

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

    machine_metrics = {}

    for machine_id, busy_time in machine_busy_time.items():

        idle_time = makespan - busy_time

        utilization = (
            busy_time / makespan
        ) * 100

        machine_metrics[machine_id] = {
            "busy": busy_time,
            "idle": idle_time,
            "utilization": utilization
        }

    return machine_metrics


# ============================================================
# SCENARIO CALCULATION
# ============================================================

def calculate_m2_scenario(schedule, reduction_percentage):
    """
    Estimate the effect of reducing M2 processing time.

    NOTE:
    This keeps the current CP-SAT schedule sequence unchanged.
    It does NOT re-run CP-SAT.
    """

    if not schedule:
        return None

    makespan = max(
        operation["end"]
        for operation in schedule
    )

    m2_busy_time = 0

    total_busy_time = {}

    for operation in schedule:

        machine_id = operation["machine_id"]

        processing_time = (
            operation["end"] - operation["start"]
        )

        if machine_id == "M2":

            reduced_processing_time = (
                processing_time
                * (1 - reduction_percentage / 100)
            )

            m2_busy_time += reduced_processing_time

        else:

            total_busy_time[machine_id] = (
                total_busy_time.get(machine_id, 0)
                + processing_time
            )

    # Add modified M2 busy time
    total_busy_time["M2"] = m2_busy_time

    # --------------------------------------------------------
    # Estimate new makespan
    # --------------------------------------------------------

    estimated_makespan = max(
        max(total_busy_time.values()),
        makespan - (
            (
                calculate_machine_metrics(schedule)["M2"]["busy"]
                - m2_busy_time
            )
        )
    )

    estimated_m2_utilization = (
        m2_busy_time / estimated_makespan
    ) * 100

    return {
        "reduction": reduction_percentage,
        "m2_busy": m2_busy_time,
        "m2_utilization": estimated_m2_utilization,
        "estimated_makespan": estimated_makespan
    }


# ============================================================
# RUN SCENARIO ANALYSIS
# ============================================================

def run_scenario_analysis(schedule):

    if not schedule:
        print("❌ No schedule available.")
        return

    print("\n========== SCENARIO ANALYSIS ==========")

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    metrics = calculate_machine_metrics(schedule)

    baseline_makespan = max(
        operation["end"]
        for operation in schedule
    )

    baseline_m2_busy = metrics["M2"]["busy"]

    baseline_m2_utilization = (
        metrics["M2"]["utilization"]
    )

    print("\n========== BASELINE ==========")

    print(
        f"Makespan          : "
        f"{baseline_makespan}"
    )

    print(
        f"M2 Busy Time      : "
        f"{baseline_m2_busy}"
    )

    print(
        f"M2 Utilization    : "
        f"{baseline_m2_utilization:.2f}%"
    )

    # --------------------------------------------------------
    # Scenarios
    # --------------------------------------------------------

    reductions = [
        10,
        20,
        30
    ]

    scenarios = []

    for reduction in reductions:

        result = calculate_m2_scenario(
            schedule,
            reduction
        )

        scenarios.append(result)

    # --------------------------------------------------------
    # Print scenario results
    # --------------------------------------------------------

    print("\n========== WHAT-IF SCENARIOS ==========")

    for scenario in scenarios:

        print(
            f"\nM2 Processing Time -"
            f"{scenario['reduction']}%"
        )

        print(
            f"M2 Busy Time      : "
            f"{scenario['m2_busy']:.2f}"
        )

        print(
            f"M2 Utilization    : "
            f"{scenario['m2_utilization']:.2f}%"
        )

        print(
            f"Estimated Makespan: "
            f"{scenario['estimated_makespan']:.2f}"
        )

    # --------------------------------------------------------
    # Visualization
    # --------------------------------------------------------

    labels = ["Baseline"] + [
        f"-{reduction}%"
        for reduction in reductions
    ]

    utilization_values = [
        baseline_m2_utilization
    ]

    makespan_values = [
        baseline_makespan
    ]

    for scenario in scenarios:

        utilization_values.append(
            scenario["m2_utilization"]
        )

        makespan_values.append(
            scenario["estimated_makespan"]
        )

    # --------------------------------------------------------
    # M2 Utilization chart
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        labels,
        utilization_values
    )

    for bar, value in zip(
        bars,
        utilization_values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 1,
            f"{value:.2f}%",
            ha="center"
        )

    plt.xlabel("Scenario")
    plt.ylabel("M2 Utilization (%)")

    plt.title(
        "Smart Job Shop Optimizer - M2 What-If Analysis"
    )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    # --------------------------------------------------------
    # Makespan chart
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        labels,
        makespan_values
    )

    for bar, value in zip(
        bars,
        makespan_values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 0.5,
            f"{value:.2f}",
            ha="center"
        )

    plt.xlabel("Scenario")
    plt.ylabel("Estimated Makespan")

    plt.title(
        "Smart Job Shop Optimizer - Scenario Makespan Analysis"
    )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.5
    )

    plt.tight_layout()

    plt.show()

    return scenarios


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== GETTING CP-SAT SCHEDULE =========="
    )

    schedule = create_schedule()

    if schedule:

        run_scenario_analysis(schedule)

    else:

        print(
            "❌ CP-SAT did not return a schedule."
        )