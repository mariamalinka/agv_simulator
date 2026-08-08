class Robot:
    def __init__(
        self,
        robot_id: int,
        start_position: tuple[int, int],
        move_delay: int = 300,
    ) -> None:

        self.id = robot_id
        self.position = start_position

        self.path: list[tuple[int, int]] = []
        self.path_index = 0

        self.move_delay = move_delay
        self.last_move_time = 0

        self.current_task = None


        # Robot state
        self.state = "idle"

        # Does the robot currently carry goods?
        self.carrying = False



    def assign_task(
        self,
        task,
        path_to_pickup: list[tuple[int, int]],
    ) -> None:
        self.current_task = task

        task.status = "assigned"

        self.state = "to_pickup"
        self.carrying = False

        self.set_path(path_to_pickup)




    def set_path(
        self,
        path: list[tuple[int, int]],
    ) -> None:
        """Give the robot a new path."""

        self.path = path
        self.path_index = 0

        if path:
            self.position = path[0]

    def update(self, current_time: int) -> None:
        """Move one step when enough time has passed."""

        if not self.path:
            return

        if self.path_index >= len(self.path) - 1:
            return

        if (
            current_time - self.last_move_time
            >= self.move_delay
        ):
            self.path_index += 1
            self.position = self.path[self.path_index]

            self.last_move_time = current_time

    def has_reached_destination(self) -> bool:
        """Check whether the robot finished its route."""

        if not self.path:
            return True

        return self.path_index >= len(self.path) - 1