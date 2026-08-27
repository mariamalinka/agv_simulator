import csv
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt


def load_results(filename: str):
    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        return list(reader)

def calculate_std(values) -> float:
    if len(values) < 2:
        return 0.0

    return statistics.stdev(values)



def calculate_summary(rows):
    groups = defaultdict(list)

    for row in rows:

        key = (
            int(row["robots"]),
            int(row["task_interval"]),
            row["dispatch_strategy"],
        )

        groups[key].append(row)

    summaries = []

    for (
        robot_count,
        task_interval,
        dispatch_strategy,
    ), group in groups.items():

        throughput_values = [
            float(row["throughput"])
            for row in group
        ]

        queue_values = [
            float(row["average_queue_time"])
            for row in group
        ]

        cycle_values = [
            float(row["average_cycle_time"])
            for row in group
        ]

        drain_values = [
            float(row["drain_time"])
            for row in group
        ]

        utilization_values = [
            float(row["fleet_utilization"])
            for row in group
        ]

        completion_values = [
            float(row["completion_rate"])
            for row in group
        ]

        distance_values = [
            float(row["distance"])
            for row in group
        ]

        avg_throughput = statistics.mean(
            throughput_values
        )

        #standard deviation
        std_throughput = calculate_std(
            throughput_values
        )

        avg_queue = statistics.mean(
            queue_values
        )

        std_queue = calculate_std(
            queue_values
        )


        avg_cycle = statistics.mean(
            cycle_values
        )

        std_cycle = calculate_std(
            cycle_values
        )

        avg_drain = statistics.mean(
            drain_values
        )

        std_drain = calculate_std(
            drain_values
        )

        avg_utilization = statistics.mean(
            utilization_values
        )

        std_utilization = calculate_std(
            utilization_values
        )

        avg_completion = statistics.mean(
            completion_values
        )

        std_completion = calculate_std(
            completion_values
        )

        avg_distance = statistics.mean(
            distance_values
        )

        std_distance = calculate_std(
            distance_values
        )

        summaries.append({
            "robots": robot_count,
            "task_interval": task_interval,
            "dispatch_strategy": dispatch_strategy,

            "average_throughput": avg_throughput,
            "std_throughput": std_throughput,

            "average_queue_time": avg_queue,
            "std_queue_time": std_queue,

            "average_cycle_time": avg_cycle,
            "std_cycle_time": std_cycle,

            "average_drain_time": avg_drain,
            "std_drain_time": std_drain,

            "average_utilization": avg_utilization,
            "std_utilization": std_utilization,

            "average_completion_rate": avg_completion,
            "std_completion_rate": std_completion,

            "average_distance": avg_distance,
            "std_distance": std_distance,

        })

    return summaries


def print_summary(summaries):

    summaries.sort(
        key=lambda x: (
            x["task_interval"],
            x["robots"],
        )
    )

    for result in summaries:

        print(
            f"Robots: {result['robots']} | "
            f"Task interval: {result['task_interval']}s | "
            f"Strategy: "
            f"{result['dispatch_strategy']}"
        )

        print(
            f"Throughput: "
            f"{result['average_throughput']:.2f} "
            f"± {result['std_throughput']:.2f}"
        )

        print(
            f"Queue time: "
            f"{result['average_queue_time']:.2f} "
            f"± {result['std_queue_time']:.2f}s"
        )

        print(
            f"Cycle time: "
            f"{result['average_cycle_time']:.2f} "
            f"± {result['std_cycle_time']:.2f}s"
        )

        print(
            f"Drain time: "
            f"{result['average_drain_time']:.2f} "
            f"± {result['std_drain_time']:.2f}s"
        )

        print(
            f"Utilization: "
            f"{result['average_utilization']:.2f} "
            f"± {result['std_utilization']:.2f}%"
        )

        print(
            f"Completion rate: "
            f"{result['average_completion_rate']:.2f} "
            f"± {result['std_completion_rate']:.2f}%"
        )

        print()



def plot_metric(
    summaries,
    metric_key,
    std_key,
    ylabel,
    title,
    filename,
    strategy,
):

    # Only keep the selected strategy
    filtered = [
        result
        for result in summaries
        if result["dispatch_strategy"]
        == strategy
    ]

    task_intervals = sorted(
        {
            result["task_interval"]
            for result in filtered
        }
    )

    for interval in task_intervals:

        # IMPORTANT:
        # use filtered, NOT summaries
        interval_results = [
            result
            for result in filtered
            if result["task_interval"]
            == interval
        ]

        interval_results.sort(
            key=lambda result:
            result["robots"]
        )

        robot_counts = [
            result["robots"]
            for result in interval_results
        ]

        values = [
            result[metric_key]
            for result in interval_results
        ]

        std_values = [
            result[std_key]
            for result in interval_results
        ]

        plt.errorbar(
            robot_counts,
            values,
            yerr=std_values,
            marker="o",
            capsize=4,
            label=f"Task every {interval}s",
        )

    plt.xlabel(
        "Number of AGVs"
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        f"{title}\n"
        f"Dispatch strategy: {strategy}"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        filename
    )

    plt.close()


def plot_strategy_comparison(
    summaries,
    task_interval,
    metric_key,
    std_key,
    ylabel,
    title,
    filename,
):

    strategies = [
        "nearest",
        "first_available",
    ]

    for strategy in strategies:

        results = [
            result
            for result in summaries
            if (
                result["task_interval"]
                == task_interval
                and
                result["dispatch_strategy"]
                == strategy
            )
        ]

        results.sort(
            key=lambda result:
            result["robots"]
        )

        robot_counts = [
            result["robots"]
            for result in results
        ]

        values = [
            result[metric_key]
            for result in results
        ]

        std_values = [
            result[std_key]
            for result in results
        ]

        plt.errorbar(
            robot_counts,
            values,
            yerr=std_values,
            marker="o",
            capsize=4,
            label=strategy,
        )

    plt.xlabel(
        "Number of AGVs"
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        f"{title}\n"
        f"Task interval = "
        f"{task_interval}s"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        filename
    )

    plt.close()




if __name__ == "__main__":

    rows = load_results(
        "results.csv"
    )



    summaries = calculate_summary(
        rows
    )

    print_summary(
        summaries
    )

    # =====================================
    # Main results - nearest strategy
    # =====================================

    plot_metric(
        summaries,
        metric_key="average_throughput",
        std_key="std_throughput",
        ylabel="Throughput [tasks/min]",
        title="AGV Fleet Size vs Throughput",
        filename="throughput_nearest.png",
        strategy="nearest",
    )

    plot_metric(
        summaries,
        metric_key="average_queue_time",
        std_key="std_queue_time",
        ylabel="Average Queue Time [s]",
        title="AGV Fleet Size vs Queue Time",
        filename="queue_time_nearest.png",
        strategy="nearest",
    )

    plot_metric(
        summaries,
        metric_key="average_cycle_time",
        std_key="std_cycle_time",
        ylabel="Average Cycle Time [s]",
        title="AGV Fleet Size vs Cycle Time",
        filename="cycle_time_nearest.png",
        strategy="nearest",
    )

    plot_metric(
        summaries,
        metric_key="average_drain_time",
        std_key="std_drain_time",
        ylabel="Average Drain Time [s]",
        title="AGV Fleet Size vs Drain Time",
        filename="drain_time_nearest.png",
        strategy="nearest",
    )

    plot_metric(
        summaries,
        metric_key="average_utilization",
        std_key="std_utilization",
        ylabel="Fleet Utilization [%]",
        title="AGV Fleet Size vs Utilization",
        filename="utilization_nearest.png",
        strategy="nearest",
    )

    plot_metric(
        summaries,
        metric_key="average_completion_rate",
        std_key="std_completion_rate",
        ylabel="Completion Rate [%]",
        title="AGV Fleet Size vs Completion Rate",
        filename="completion_rate_nearest.png",
        strategy="nearest",
    )

    # =====================================
    # Dispatch strategy comparison
    # =====================================

    plot_strategy_comparison(
        summaries,
        task_interval=10,
        metric_key="average_cycle_time",
        std_key="std_cycle_time",
        ylabel="Average Cycle Time [s]",
        title="Dispatch Strategy Comparison",
        filename="strategy_cycle_time_10s.png",
    )

    plot_strategy_comparison(
        summaries,
        task_interval=10,
        metric_key="average_distance",
        std_key="std_distance",
        ylabel="Total Travel Distance [cells]",
        title="Dispatch Strategy vs Travel Distance",
        filename="strategy_distance_10s.png",
    )