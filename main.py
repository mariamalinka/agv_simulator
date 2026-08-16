import sys

import pygame
import random

from warehouse import (
    create_default_warehouse,
    PICKUP_POSITIONS,
    DELIVERY_POSITIONS,
)
from pathfinding import astar

from renderer import (
    CELL_SIZE,
    PANEL_WIDTH,
    BACKGROUND_COLOR,
    draw_warehouse,
    draw_robot,
    draw_dashboard,
)

from robot import Robot

from task import Task

from dispatcher import assign_waiting_tasks
from metrics import save_results


def find_yield_position(
    robot,
    robots,
    warehouse,
    proposed_positions,
):
    blocked_positions = {
        other_robot.position
        for other_robot in robots
        if other_robot.id != robot.id
    }

    # Also avoid cells that other robots
    # are planning to enter.
    blocked_positions.update(
        proposed_positions[other_robot.id]
        for other_robot in robots
        if other_robot.id != robot.id
    )

    for position in warehouse.get_neighbors(
        robot.position
    ):
        if position not in blocked_positions:
            return position

    return None

def main() -> None:
    pygame.init()

    # ------------------------
    # Create warehouse
    # ------------------------

    warehouse = create_default_warehouse()

    start = (1, 1)

    tasks = [
        Task(
            id=1,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[0],
        ),

        Task(
            id=2,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[1],
        ),

        Task(
            id=3,
            pickup=PICKUP_POSITIONS[0],
            delivery=DELIVERY_POSITIONS[1],
        ),

        Task(
            id=4,
            pickup=PICKUP_POSITIONS[1],
            delivery=DELIVERY_POSITIONS[0],
        ),
    ]

    current_task_index = 0

    # ------------------------
    # Calculate robot route
    # ------------------------

    task = tasks[current_task_index]

    robots = [
        Robot(
            robot_id=1,
            start_position=(1, 1),
            color=(50, 120, 220),  # blue
        ),

        Robot(
            robot_id=2,
            start_position=(13, 18),
            color=(180, 80, 200),  # purple
        ),
    ]

    assign_waiting_tasks(
        robots,
        tasks,
        warehouse,
    )
    
    

    # ------------------------
    # Create Pygame window
    # ------------------------

    warehouse_width = (
        warehouse.columns * CELL_SIZE
    )

    window_width = (
        warehouse_width + PANEL_WIDTH
    )

    window_height = (
        warehouse.rows * CELL_SIZE
    )

    screen = pygame.display.set_mode(
        (window_width, window_height)
    )

    pygame.display.set_caption(
        "AGV Warehouse Simulator"
    )

    clock = pygame.time.Clock()



    running = True

    # ------------------------
    # Main simulation loop
    # ------------------------

    MOVE_DELAY = 300
    last_move_time = pygame.time.get_ticks()

    collisions_avoided = 0

    TASK_GENERATION_DELAY = 5000  # milliseconds
    last_task_generation_time = pygame.time.get_ticks()

    next_task_id = len(tasks) + 1

    while running:

        # ========================================
        # 1. HANDLE PYGAME EVENTS
        # ========================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


        # ========================================
        # 2. GET CURRENT TIME
        # ========================================

        current_time = pygame.time.get_ticks()

        if (
            current_time - last_task_generation_time
            >= TASK_GENERATION_DELAY
        ):
            pickup = random.choice(PICKUP_POSITIONS)
            delivery = random.choice(DELIVERY_POSITIONS)

            new_task = Task(
                id=next_task_id,
                pickup=pickup,
                delivery=delivery,
            )

            tasks.append(new_task)

            print(
                f"New Task {new_task.id}: "
                f"{pickup} -> {delivery}"
            )

            next_task_id += 1
            last_task_generation_time = current_time


        # ========================================
        # 3. MOVE ROBOTS
        # ========================================

        if current_time - last_move_time >= MOVE_DELAY:

            # First ask every robot:
            # "Where do you want to move next?"
            proposed_positions = {}

            for robot in robots:
                proposed_positions[robot.id] = (
                    robot.get_next_position()
                )


            # Now decide which robots are allowed to move
            for robot in robots:

                next_position = proposed_positions[robot.id]

                collision = False
                should_replan = False

                # Compare this robot with every other robot
                for other_robot in robots:

                    # Don't compare robot with itself
                    if robot.id == other_robot.id:
                        continue

                    other_next_position = (
                        proposed_positions[other_robot.id]
                    )


                    # --------------------------------
                    # Collision type 1:
                    # Both robots want the same cell
                    # --------------------------------

                    if (
                        next_position == other_robot.position
                        and other_next_position == robot.position
                    ):
                        collision = True

                        # Higher ID yields
                        if robot.id > other_robot.id:

                            yield_position = find_yield_position(
                                robot,
                                robots,
                                warehouse,
                                proposed_positions,
                            )

                            if yield_position is not None:

                                print(
                                    f"Robot {robot.id} yields "
                                    f"from {robot.position} "
                                    f"to {yield_position}"
                                )

                                robot.position = yield_position
                                robot.distance_travelled += 1

                                # Work out where it ultimately
                                # still needs to go.
                                if robot.state == "to_pickup":
                                    goal = robot.current_task.pickup

                                elif robot.state == "to_delivery":
                                    goal = robot.current_task.delivery

                                else:
                                    goal = None

                                if goal is not None:

                                    blocked_positions = {
                                        r.position
                                        for r in robots
                                        if r.id != robot.id
                                    }

                                    new_path = astar(
                                        warehouse,
                                        robot.position,
                                        goal,
                                        blocked_positions,
                                    )

                                    if new_path:
                                        robot.set_path(new_path)
                                        robot.replan_count += 1

                                robot.reset_wait()

                        break


                    # --------------------------------
                    # Collision type 2:
                    # Another robot is staying
                    # in the cell we want
                    # --------------------------------

                    if (
                        next_position == other_robot.position
                        and
                        other_next_position == other_robot.position
                    ):
                        collision = True
                        collisions_avoided += 1
                        should_replan = True
                        break


                    # --------------------------------
                    # Collision type 3:
                    # Robots want to swap positions
                    # --------------------------------

                    if (
                        next_position == other_robot.position
                        and
                        other_next_position == robot.position
                    ):
                        collision = True
                        collisions_avoided += 1

                        # Only the robot with the higher ID
                        # is responsible for finding another route.
                        if robot.id > other_robot.id:
                            should_replan = True

                        break


                # Move only when there is no collision
                if not collision:
                    robot.move_one_step()
                    robot.reset_wait()

                else:
                    if should_replan:
                        robot.add_wait()

                    else:
                        robot.reset_wait()

                    if should_replan and robot.wait_steps >= 3:

                        blocked_positions = {
                            other_robot.position
                            for other_robot in robots
                            if other_robot.id != robot.id
                            }

                        if robot.current_task is not None:

                            if robot.state == "to_pickup":
                                goal = robot.current_task.pickup

                            elif robot.state == "to_delivery":
                                goal = robot.current_task.delivery

                            else:
                                goal = None

                            if goal is not None:

                                new_path = astar(
                                    warehouse,
                                    robot.position,
                                    goal,
                                    blocked_positions,
                                )

                                if new_path:
                                    robot.set_path(new_path)

                                    robot.replan_count += 1

                                    print(
                                            f"Robot {robot.id} yielded and replanned."
                                        )

                        robot.reset_wait()


            # Reset movement timer
            last_move_time = current_time


        # ========================================
        # 4. CHECK ROBOT TASK STATES
        # ========================================

        for robot in robots:

            # --------------------------------
            # Robot reached pickup
            # --------------------------------

            if (
                robot.state == "to_pickup"
                and robot.position == robot.current_task.pickup
            ):
                print(
                    f"Robot {robot.id} reached pickup!"
                )

                # Robot now has the package
                robot.carrying = True

                robot.current_task.status = "picked_up"

                # Calculate route to delivery
                path_to_delivery = astar(
                    warehouse,
                    robot.position,
                    robot.current_task.delivery,
                )

                robot.state = "to_delivery"

                robot.set_path(
                    path_to_delivery
                )


            # --------------------------------
            # Robot reached delivery
            # --------------------------------

            elif (
                robot.state == "to_delivery"
                and robot.position == robot.current_task.delivery
            ):
                print(
                    f"Robot {robot.id} completed "
                    f"Task {robot.current_task.id}!"
                )

                robot.current_task.status = "completed"

                # Drop package
                robot.carrying = False

                # Robot becomes available again
                robot.state = "idle"

                robot.current_task = None

        assign_waiting_tasks(
                robots,
                tasks,
                warehouse,
            )


        # ========================================
        # 5. DRAW EVERYTHING
        # ========================================

        screen.fill(BACKGROUND_COLOR)

        draw_warehouse(
            screen,
            warehouse,
        )

        # Draw every robot
        for robot in robots:
            draw_robot(
                screen,
                robot.position,
                robot.color,
                robot.carrying,
            )

        draw_dashboard(
            screen,
            robots,
            tasks,
            warehouse_width,
        )

        pygame.display.flip()


        # ========================================
        # 6. LIMIT PYGAME TO 60 FPS
        # ========================================

        clock.tick(60)

    save_results(
    "results.csv",
    robots,
    tasks,
    collisions_avoided,
)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()