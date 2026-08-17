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
from metrics import save_results


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
    ) -> None:
        self.screen = screen
        self.warehouse = warehouse
        self.robots = robots
        self.tasks = tasks

        self.reservations = reservations
        self.simulation_step = simulation_step

        self.warehouse_width = warehouse_width

        self.clock = pygame.time.Clock()

        # One simulation movement step every 300 ms.
        self.move_delay = 300
        self.last_move_time = pygame.time.get_ticks()

        # Generate one new task every 5 seconds.
        self.task_generation_delay = 5000
        self.last_task_generation_time = (
            pygame.time.get_ticks()
        )

        self.next_task_id = len(tasks) + 1

        # Kept only because the current metrics.py
        # still expects this argument.
        #
        # With reservation planning, conflicts are
        # prevented during planning rather than by
        # the old reactive collision code.
        self.collisions_avoided = 0

        self.running = True

    # ==================================================
    # TASK GENERATION
    # ==================================================

    def generate_task_if_needed(
        self,
        current_time: int,
    ) -> None:
        if (
            current_time
            - self.last_task_generation_time
            < self.task_generation_delay
        ):
            return

        pickup = random.choice(
            PICKUP_POSITIONS
        )

        delivery = random.choice(
            DELIVERY_POSITIONS
        )

        new_task = Task(
            id=self.next_task_id,
            pickup=pickup,
            delivery=delivery,
        )

        self.tasks.append(new_task)

        print(
            f"New Task {new_task.id}: "
            f"{pickup} -> {delivery}"
        )

        self.next_task_id += 1

        self.last_task_generation_time = (
            current_time
        )

    # ==================================================
    # MOVEMENT
    # ==================================================

    def move_robots_if_needed(
        self,
        current_time: int,
    ) -> None:
        if (
            current_time - self.last_move_time
            < self.move_delay
        ):
            return

        # The paths were already coordinated by
        # Space-Time A*, so robots can now simply
        # execute one planned step.
        for robot in self.robots:
            robot.move_one_step()

        self.simulation_step += 1

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

                robot.current_task.status = (
                    "completed"
                )

                robot.carrying = False
                robot.state = "idle"
                robot.current_task = None

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
        )

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
        )

        pygame.display.flip()

    # ==================================================
    # MAIN LOOP
    # ==================================================

    def run(self) -> None:
        while self.running:

            # ------------------------------
            # Events
            # ------------------------------
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif (
                    event.type
                    == pygame.KEYDOWN
                    and event.key
                    == pygame.K_ESCAPE
                ):
                    self.running = False

            current_time = (
                pygame.time.get_ticks()
            )

            # ------------------------------
            # Generate new work
            # ------------------------------
            self.generate_task_if_needed(
                current_time
            )

            # ------------------------------
            # Execute planned movement
            # ------------------------------
            self.move_robots_if_needed(
                current_time
            )

            # ------------------------------
            # Check whether goals changed
            # ------------------------------
            needs_replan = (
                self.update_task_states()
            )

            # ------------------------------
            # Assign waiting tasks
            # ------------------------------
            assignment_changed = (
                self.assign_waiting_tasks()
            )

            if assignment_changed:
                needs_replan = True

            # ------------------------------
            # Recalculate coordinated paths
            # only when necessary
            # ------------------------------
            if needs_replan:
                self.replan()

            # ------------------------------
            # Draw
            # ------------------------------
            self.draw()

            self.clock.tick(60)

        # ------------------------------
        # Save results on exit
        # ------------------------------
        save_results(
            "results.csv",
            self.robots,
            self.tasks,
            self.collisions_avoided,
        )

    def check_collisions(
        self,
        old_positions,
    ) -> None:
        """Verify that the planned movements are collision-free."""

        # --------------------------------
        # Same-cell collision
        # --------------------------------
        positions = [
            robot.position
            for robot in self.robots
        ]

        if len(positions) != len(set(positions)):
            raise RuntimeError(
                "Collision: two robots occupy the same cell!"
            )

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