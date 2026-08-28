from reservation import ReservationTable


def test_path_reserves_cells_and_edge():
    reservations = ReservationTable()

    path = [
        (1, 1),
        (1, 2),
        (1, 3),
    ]

    reservations.reserve_path(
        path,
        start_time=10,
    )

    assert reservations.is_cell_reserved(
        (1, 1),
        10,
    )

    assert reservations.is_cell_reserved(
        (1, 2),
        11,
    )

    assert reservations.is_cell_reserved(
        (1, 3),
        12,
    )

    assert reservations.is_edge_reserved(
        (1, 1),
        (1, 2),
        11,
    )


def test_destination_can_be_held():
    reservations = ReservationTable()

    path = [
        (1, 1),
        (1, 2),
    ]

    reservations.reserve_path(
        path,
        start_time=0,
        hold_until=3,
    )

    assert reservations.is_cell_reserved(
        (1, 2),
        1,
    )

    assert reservations.is_cell_reserved(
        (1, 2),
        2,
    )

    assert reservations.is_cell_reserved(
        (1, 2),
        3,
    )

