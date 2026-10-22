class Robot:
    def __init__(
        self,
        robot_id: int,
        start_position: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:

        self.id = robot_id
        self.position = start_position
        self.home_position = start_position
        self.color = color

        self.path: list[tuple[int, int]] = []
        self.path_index = 0

        self.current_task = None


        # Robot state
        self.state = "idle"

        # Does the robot currently carry goods?
        self.carrying = False

        self.distance_travelled = 0
        self.total_wait_steps = 0
        self.plans_created = 0
        self.idle_steps = 0

        



    def assign_task(
        self,
        task
    ) -> None:
        self.current_task = task

        task.status = "assigned"

        self.state = "to_pickup"
        self.carrying = False

        self.path = []
        self.path_index = 0

       

        




    def set_path(
        self,
        path: list[tuple[int, int]],
    ) -> None:
        """Assign a new path without moving the robot."""

        if (
            path
            and path[0] != self.position
        ):
            raise RuntimeError(
                f"Robot {self.id}: "
                f"path starts at {path[0]}, "
                f"but robot is at {self.position}"
            )

        self.path = path
        self.path_index = 0

    def move_one_step(self) -> None:
        """Move one position along the planned path."""

        # ---------------------------------
        # Truly idle robot
        # ---------------------------------
        if self.state == "idle":
            self.idle_steps += 1
            return

        # ---------------------------------
        # Robot wants to move but currently
        # has no usable path
        # ---------------------------------
        if not self.path:

            # Count task-related waiting only
            if self.current_task is not None:
                self.total_wait_steps += 1

            return

        # ---------------------------------
        # End of current path
        # ---------------------------------
        if self.path_index >= len(self.path) - 1:

            if self.current_task is not None:
                self.total_wait_steps += 1

            return

        old_position = self.position

        # Follow next planned position
        self.path_index += 1

        self.position = self.path[
            self.path_index
        ]

        # ---------------------------------
        # Actual movement
        # ---------------------------------
        if self.position != old_position:
            self.distance_travelled += 1

        # ---------------------------------
        # Space-Time A* planned a WAIT
        # ---------------------------------
        elif self.current_task is not None:
            self.total_wait_steps += 1





    