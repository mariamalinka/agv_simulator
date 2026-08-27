from dataclasses import dataclass

from config import SimulationConfig


@dataclass
class SimulationResult:
    experiment_id: str

    robots: int
    random_seed: int

    simulation_duration: int
    simulated_time: int
    task_interval: int

    dispatch_strategy: str

    tasks_generated: int
    completed_tasks: int
    waiting_tasks: int

    throughput: float

    distance: int
    wait_steps: int
    idle_steps: int
    plans_created: int

    average_queue_time: float
    average_cycle_time: float

    completed_by_horizon: int
    drain_time: int
    fleet_utilization: float
    completion_rate: float

def calculate_average_queue_time(tasks) -> float:
    values = [
        task.assigned_at - task.created_at
        for task in tasks
        if task.assigned_at is not None
    ]

    if not values:
        return 0.0

    return sum(values) / len(values)


def calculate_average_cycle_time(tasks) -> float:
    values = [
        task.completed_at - task.created_at
        for task in tasks
        if task.completed_at is not None
    ]

    if not values:
        return 0.0

    return sum(values) / len(values)


def build_simulation_result(
    robots,
    tasks,
    config: SimulationConfig,
    simulation_time: int,
) -> SimulationResult:

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == "completed"
    )

    waiting_tasks = sum(
        1
        for task in tasks
        if task.status == "waiting"
    )

    total_distance = sum(
        robot.distance_travelled
        for robot in robots
    )

    total_wait_steps = sum(
        robot.total_wait_steps
        for robot in robots
    )

    total_idle_steps = sum(
        robot.idle_steps
        for robot in robots
    )

    total_plans = sum(
        robot.plans_created
        for robot in robots
    )

    completed_by_horizon = sum(
        1
        for task in tasks
        if (
            task.completed_at is not None
            and task.completed_at
            <= config.simulation_duration
        )
    )

    experiment_minutes = (
        config.simulation_duration / 60
    )

    throughput = (
        completed_by_horizon
        / experiment_minutes
    )

    drain_time = max(
        0,
        simulation_time
        - config.simulation_duration,
    )



    avg_queue_time = calculate_average_queue_time(
        tasks
    )

    avg_cycle_time = calculate_average_cycle_time(
        tasks
    )


    horizon = config.simulation_duration

    busy_robot_time = 0

    for task in tasks:

        if task.assigned_at is None:
            continue

        # Task was not assigned during the
        # official experiment period.
        if task.assigned_at >= horizon:
            continue

        if task.completed_at is None:
            busy_end = horizon
        else:
            busy_end = min(
                task.completed_at,
                horizon,
            )

        busy_robot_time += max(
            0,
            busy_end - task.assigned_at,
        )

    available_robot_time = (
        len(robots) * horizon
    )

    if available_robot_time > 0:
        fleet_utilization = (
            busy_robot_time
            / available_robot_time
            * 100
        )
    else:
        fleet_utilization = 0.0


    if len(tasks) > 0:
        completion_rate = (
            completed_by_horizon
            / len(tasks)
            * 100
        )
    else:
        completion_rate = 0.0

    experiment_id = (
        f"R{len(robots)}_"
        f"S{config.random_seed}_"
        f"I{config.task_generation_interval}_"
        f"D{config.dispatch_strategy}"
    )

    return SimulationResult(
        experiment_id=experiment_id,

        robots=len(robots),
        random_seed=config.random_seed,

        simulation_duration=(
            config.simulation_duration
        ),

        simulated_time=simulation_time,

        task_interval=(
            config.task_generation_interval
        ),

        dispatch_strategy=config.dispatch_strategy,

        tasks_generated=len(tasks),
        completed_tasks=completed_tasks,
        completed_by_horizon=completed_by_horizon,
        waiting_tasks=waiting_tasks,

        throughput=throughput,

        distance=total_distance,
        wait_steps=total_wait_steps,
        idle_steps=total_idle_steps,
        plans_created=total_plans,

        average_queue_time=avg_queue_time,
        average_cycle_time=avg_cycle_time,
        drain_time=drain_time,
        fleet_utilization=fleet_utilization,
        completion_rate=completion_rate,

        
    )