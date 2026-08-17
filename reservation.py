class ReservationTable:
    def __init__(self) -> None:
        # (position, time)
        self.cells = set()

        # (from_position, to_position, time)
        self.edges = set()

    def reserve_path(
        self,
        path: list[tuple[int, int]],
        start_time: int = 0,
        hold_until: int | None = None,
    ) -> None:

        if not path:
            return

        for index, position in enumerate(path):
            time = start_time + index

            # Reserve cell
            self.cells.add(
                (position, time)
            )

            # Reserve movement edge
            if index > 0:
                previous = path[index - 1]

                self.edges.add(
                    (
                        previous,
                        position,
                        time,
                    )
                )

        # Keep the destination occupied
        # after the robot arrives.
        if hold_until is not None:

            goal = path[-1]
            arrival_time = (
                start_time + len(path) - 1
            )

            for time in range(
                arrival_time + 1,
                hold_until + 1,
            ):
                self.cells.add(
                    (goal, time)
                )

    def is_cell_reserved(
        self,
        position: tuple[int, int],
        time: int,
    ) -> bool:

        return (
            position,
            time,
        ) in self.cells

    def is_edge_reserved(
        self,
        from_position: tuple[int, int],
        to_position: tuple[int, int],
        time: int,
    ) -> bool:

        return (
            from_position,
            to_position,
            time,
        ) in self.edges