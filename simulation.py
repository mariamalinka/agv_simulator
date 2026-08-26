import random

import pygame

from warehouse import (
    PICKUP_POSITIONS,
    DELIVERY_POSITIONS,
)

from task import Task
from dispatcher import assign_waiting_tasks
from planner import replan_all_robots
from renderer import (
    BACKGROUND_COLOR,
    draw_warehouse,
    draw_robot,
    draw_dashboard,
)

from config import SimulationConfig

from results import (
    SimulationResult,
    build_simulation_result,
)


class Simulation:
    def __init__(
        self,
        screen,
        warehouse,
        robots,
        tasks,
        reservations,
        simulation_step,
        warehouse_width,
        config: SimulationConfig,
    ) -> None:


        self.screen = screen
        self.warehouse = warehouse
        self.robots = robots
        self.tasks = tasks

        self.reservations = reservations
        self.simulation_step = simulation_step
        self.warehouse_width = warehouse_width

        self.config = config

        # -------------------------
        # Simulation state
        # -------------------------

        self.simulation_time = 0
        self.next_task_id = len(tasks) + 1

        self.next_task_generation_time = (
            config.task_generation_interval
        )

        self.random_generator = random.Random(
            config.random_seed
        )

        self.visual = config.visual
        self.move_delay = config.move_delay

        self.running = True

        self.clock = pygame.time.Clock()
        self.last_move_time = pygame.time.get_ticks()

        self.last_stuck_replan_step = -1
        self.replan_number = 0
        

    # ==================================================
    # TASK GENERATION
    # ==================================================

    def generate_task_if_needed(
        self
    ) -> None:

        if (
            self.simulation_time
            >= self.config.simulation_duration
        ):        
            return

        if (
            self.simulation_time
            < self.next_task_generation_time
        ):
            return

        pickup = self.random_generator.choice(
            PICKUP_POSITIONS
        )

        delivery = self.random_generator.choice(
            DELIVERY_POSITIONS
        )

        new_task = Task(
            id=self.next_task_id,
            pickup=pickup,
            delivery=delivery,
            created_at=self.simulation_time,
        )

        self.tasks.append(new_task)

        print(
            f"New Task {new_task.id}: "
            f"{pickup} -> {delivery}"
        )

        self.next_task_id += 1

        self.next_task_generation_time += (
            self.config.task_generation_interval
        )

    # ==================================================
    # MOVEMENT
    # ==================================================

    def move_robots_if_needed(
        self,
        current_time: int,
    ) -> None:
        if self.visual:
            if (
                current_time - self.last_move_time
                < self.move_delay
            ):
                return

            # Remember positions before movement
        old_positions = {
            robot.id: robot.position
            for robot in self.robots
        }

        # The paths were already coordinated by
        # Space-Time A*, so robots can now simply
        # execute one planned step.
        for robot in self.robots:
            robot.move_one_step()

        self.check_collisions(
            old_positions
        )

        self.simulation_step += 1
        self.simulation_time += 1

        if self.visual:
            self.last_move_time = current_time

    # ==================================================
    # PICKUP / DELIVERY
    # ==================================================

    def update_task_states(self) -> bool:
        """
        Returns True when robot goals changed and
        coordinated replanning is therefore required.
        """

        needs_replan = False

        for robot in self.robots:

            # Robot reached its parking position
            if (
                robot.state == "to_parking"
                and robot.position == robot.home_position
            ):
                robot.state = "idle"

                print(
                    f"Robot {robot.id} reached parking."
                )

                needs_replan = True

                continue

            if robot.current_task is None:
                continue

            # ------------------------------
            # Reached pickup
            # ------------------------------
            if (
                robot.state == "to_pickup"
                and robot.position
                == robot.current_task.pickup
            ):
                print(
                    f"Robot {robot.id} "
                    f"reached pickup!"
                )

                robot.carrying = True

                robot.current_task.status = (
                    "picked_up"
                )
                robot.current_task.picked_up_at = (
                self.simulation_time
            )

                # Important:
                # Do NOT calculate normal A* here.
                #
                # We only change the goal.
                # replan_all_robots() will calculate
                # coordinated routes afterwards.
                robot.state = "to_delivery"

                needs_replan = True

            # ------------------------------
            # Reached delivery
            # ------------------------------
            elif (
                robot.state == "to_delivery"
                and robot.position
                == robot.current_task.delivery
            ):
                completed_task_id = (
                    robot.current_task.id
                )

                print(
                    f"Robot {robot.id} completed "
                    f"Task {completed_task_id}!"
                )

                robot.current_task.status = "completed"
                robot.current_task.completed_at = self.simulation_time

                robot.carrying = False
                robot.current_task = None

                # Move away from the delivery point
                if robot.position != robot.home_position:
                    robot.state = "to_parking"
                else:
                    robot.state = "idle"

                needs_replan = True

        return needs_replan

    # ==================================================
    # DISPATCHING
    # ==================================================

    def assign_waiting_tasks(self) -> bool:
        """
        Run the existing dispatcher and detect whether
        any robot received a different task.

        This lets us replan only when assignments
        actually changed.
        """

        before = {
            robot.id: (
                robot.current_task.id
                if robot.current_task is not None
                else None
            )
            for robot in self.robots
        }

        assign_waiting_tasks(
            self.robots,
            self.tasks,
            self.warehouse,
            self.simulation_time,
            
        )
        

        after = {
            robot.id: (
                robot.current_task.id
                if robot.current_task is not None
                else None
            )
            for robot in self.robots
        }
        

        return before != after

    # ==================================================
    # COORDINATED REPLANNING
    # ==================================================

    def replan(self) -> None:
        self.reservations = replan_all_robots(
            self.robots,
            self.warehouse,
            self.simulation_step,
            priority_offset=self.replan_number,
        )
        self.replan_number += 1

    # ==================================================
    # RENDERING
    # ==================================================

    def draw(self) -> None:
        self.screen.fill(
            BACKGROUND_COLOR
        )

        draw_warehouse(
            self.screen,
            self.warehouse,
        )

        for robot in self.robots:
            draw_robot(
                self.screen,
                robot.position,
                robot.color,
                robot.carrying,
            )

        draw_dashboard(
            self.screen,
            self.robots,
            self.tasks,
            self.warehouse_width,
            self.simulation_time,
            self.config.simulation_duration,
            self.get_throughput(),
            
        )

        pygame.display.flip()

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self) -> SimulationResult:
        while self.running:

            # ------------------------------
            # 1. Handle events
            # ------------------------------
            if self.visual:
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        self.running = False

                    elif (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE
                    ):
                        self.running = False

            current_time = pygame.time.get_ticks()

            # ------------------------------
            # 2. Generate new tasks
            # ------------------------------
            # generate_task_if_needed()
            # must stop creating tasks after
            # simulation_duration
            self.generate_task_if_needed()

            # ------------------------------
            # 3. Move robots
            # ------------------------------
            self.move_robots_if_needed(
                current_time
            )

            # ------------------------------
            # 4. Check pickup/delivery
            # ------------------------------
            needs_replan = (
                self.update_task_states()
            )

            # ------------------------------
            # 5. Assign waiting tasks
            # ------------------------------
            assignment_changed = (
                self.assign_waiting_tasks()
            )

            if assignment_changed:
                needs_replan = True

            # ------------------------------
            # 6. Replan if something changed
            # ------------------------------
            if (
                self.has_stuck_robots()
                and self.simulation_step
                % self.config.replan_interval == 0
                and self.simulation_step
                != self.last_stuck_replan_step
            ):
                needs_replan = True

                self.last_stuck_replan_step = (
                    self.simulation_step
                )

                
            if needs_replan:
                self.replan()

            # ------------------------------
            # 7. Normal finish after draining
            # ------------------------------
            if (
                self.simulation_time
                >= self.config.simulation_duration
                and self.all_work_finished()
            ):
                print(
                    f"Simulation finished after draining "
                    f"at {self.simulation_time}s!"
                )

                self.running = False

            # ------------------------------
            # 8. Emergency stop
            # ------------------------------
            elif (
                self.simulation_time
                >= (
                    self.config.simulation_duration
                    + self.config.max_drain_time
                )
            ):
                print(
                    "WARNING: maximum drain time reached."
                )

                self.running = False

            # ------------------------------
            # 9. Draw
            # ------------------------------
            if self.visual:
                self.draw()
                self.clock.tick(60)

        # ------------------------------
        # 10. Return results
        # ------------------------------
        return build_simulation_result(
            robots=self.robots,
            tasks=self.tasks,
            config=self.config,
            simulation_time=self.simulation_time,
        )

    def check_collisions(
        self,
        old_positions,
    ) -> None:
        """Verify that the planned movements are collision-free."""

        # --------------------------------
        # Same-cell collision
        # --------------------------------
        positions = {}

        for robot in self.robots:

            if robot.position in positions:

                other_robot_id = positions[
                    robot.position
                ]

                raise RuntimeError(
                    f"Collision at {robot.position}: "
                    f"Robot {other_robot_id} and "
                    f"Robot {robot.id}"
                )

            positions[robot.position] = robot.id

        # --------------------------------
        # Swap collision
        # --------------------------------
        for robot in self.robots:
            for other_robot in self.robots:

                if robot.id >= other_robot.id:
                    continue

                swapped = (
                    robot.position
                    == old_positions[other_robot.id]
                    and
                    other_robot.position
                    == old_positions[robot.id]
                )

                if swapped:
                    raise RuntimeError(
                        f"Swap collision between "
                        f"Robot {robot.id} and "
                        f"Robot {other_robot.id}!"
                    )



    def get_throughput(self) -> float:

        completed_by_horizon = sum(
            1
            for task in self.tasks
            if (
                task.completed_at is not None
                and task.completed_at
                <= self.config.simulation_duration
            )
        )

        experiment_minutes = (
            self.config.simulation_duration / 60
        )

        if experiment_minutes == 0:
            return 0.0

        return (
            completed_by_horizon
            / experiment_minutes
        )


    def all_work_finished(self) -> bool:
        tasks_finished = all(
            task.status == "completed"
            for task in self.tasks
        )

        robots_idle = all(
            robot.current_task is None
            for robot in self.robots
        )

        return tasks_finished and robots_idle


    def has_stuck_robots(self) -> bool:

        for robot in self.robots:

            # Idle robot is allowed to stay still
            if robot.current_task is None:
                continue

            if robot.state == "to_pickup":
                goal = robot.current_task.pickup

            elif robot.state == "to_delivery":
                goal = robot.current_task.delivery

            else:
                continue

            path_finished = (
                not robot.path
                or robot.path_index
                >= len(robot.path) - 1
            )

            # Robot still has somewhere to go,
            # but it has no route left.
            if (
                path_finished
                and robot.position != goal
            ):
                return True

        return False

