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

from config import (
    SIMULATION_DURATION,
    TASK_GENERATION_INTERVAL,
    MOVE_DELAY,
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
        random_seed=42,
        visual=True,
    ) -> None:

        
        self.screen = screen
        self.warehouse = warehouse

        # IMPORTANT
        self.robots = robots
        self.tasks = tasks

        self.reservations = reservations
        self.simulation_step = simulation_step
        self.warehouse_width = warehouse_width
        self.clock = pygame.time.Clock()

        # Visual movement speed
        self.move_delay = MOVE_DELAY
        self.last_move_time = pygame.time.get_ticks()

        # Random generator for reproducible experiments
        self.random_seed = random_seed

        self.random_generator = random.Random(
            random_seed
        )

        # Generate one task every 15 simulated seconds
        self.task_generation_interval = (
            TASK_GENERATION_INTERVAL
        )

        self.next_task_generation_time = (
            TASK_GENERATION_INTERVAL
        )

        self.next_task_id = len(tasks) + 1

        self.running = True

        # Simulated experiment time
        self.simulation_time = 0
        self.simulation_duration = (
            SIMULATION_DURATION
        )
        self.visual = visual

        

    # ==================================================
    # TASK GENERATION
    # ==================================================

    def generate_task_if_needed(
        self
    ) -> None:
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
            self.task_generation_interval
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

                robot.current_task.status = (
                    "completed"
                )

                robot.current_task.completed_at = (
                self.simulation_time
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
            self.simulation_time,
            self.simulation_duration,
            self.get_throughput(),
            
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
            if self.visual:
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
            self.generate_task_if_needed()

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

            if self.simulation_time >= self.simulation_duration:
                print("Simulation finished!")
                self.running = False

            # ------------------------------
            # Draw
            # ------------------------------
            if self.visual:
                self.draw()
                self.clock.tick(60)

        # ------------------------------
        # Save results on exit
        # ------------------------------
        save_results(
            "results.csv",
            self.robots,
            self.tasks,
            self.random_seed,
            self.simulation_duration,
            self.get_throughput(),
           
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
        completed_tasks = sum(
            1
            for task in self.tasks
            if task.status == "completed"
        )

        if self.simulation_time == 0:
            return 0.0

        simulated_minutes = (
            self.simulation_time / 60
        )

        return (
            completed_tasks
            / simulated_minutes
        )

