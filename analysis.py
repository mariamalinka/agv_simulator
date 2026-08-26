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
        )

        groups[key].append(row)

    summaries = []

    for (
        robot_count,
        task_interval,
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

        summaries.append({
            "robots": robot_count,
            "task_interval": task_interval,

            "average_throughput": avg_throughput,
            "std_throughput": std_throughput,

            "average_queue_time": avg_queue,
            "std_queue_time": std_queue,

            "average_cycle_time": avg_cycle,
            "std_cycle_time": std_cycle,
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
            f"Task interval: {result['task_interval']}s"
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

        print()



def plot_metric(
    summaries,
    metric_key,
    std_key,
    ylabel,
    title,
    filename,
):
    task_intervals = sorted({
        result["task_interval"]
        for result in summaries
    })

    for task_interval in task_intervals:

        filtered = [
            result
            for result in summaries
            if result["task_interval"] == task_interval
        ]

        filtered.sort(
            key=lambda result: result["robots"]
        )

        robot_counts = [
            result["robots"]
            for result in filtered
        ]

        values = [
            result[metric_key]
            for result in filtered
        ]

        errors = [
            result[std_key]
            for result in filtered
        ]

        plt.errorbar(
            robot_counts,
            values,
            yerr=errors,
            marker="o",
            capsize=4,
            label=f"Task every {task_interval}s",
        )

    plt.xlabel("Number of AGVs")
    plt.ylabel(ylabel)
    plt.title(title)

    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(filename)

    plt.show()

    # Very important:
    # clear the figure before creating another graph
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

    plot_metric(
    summaries,
    metric_key="average_throughput",
    std_key="std_throughput",
    ylabel="Throughput [tasks/min]",
    title="AGV Fleet Size vs Throughput",
    filename="throughput.png",
)

    plot_metric(
        summaries,
        metric_key="average_queue_time",
        std_key="std_queue_time",
        ylabel="Average Queue Time [s]",
        title="AGV Fleet Size vs Queue Time",
        filename="queue_time.png",
    )

    plot_metric(
        summaries,
        metric_key="average_cycle_time",
        std_key="std_cycle_time",
        ylabel="Average Cycle Time [s]",
        title="AGV Fleet Size vs Cycle Time",
        filename="cycle_time.png",
    )   