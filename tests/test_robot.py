import pytest

from robot import Robot


def make_robot():
    return Robot(
        robot_id=1,
        start_position=(1, 1),
        color=(0, 0, 0),
    )


def test_idle_robot_does_not_move():
    robot = make_robot()

    robot.state = "idle"

    robot.set_path([
        (1, 1),
        (1, 2),
    ])

    robot.move_one_step()

    assert robot.position == (1, 1)


def test_parking_robot_can_move():
    robot = make_robot()

    robot.state = "to_parking"
    robot.current_task = None

    robot.set_path([
        (1, 1),
        (1, 2),
    ])

    robot.move_one_step()

    assert robot.position == (1, 2)


def test_path_must_start_at_robot_position():
    robot = make_robot()

    with pytest.raises(RuntimeError):
        robot.set_path([
            (5, 5),
            (5, 6),
        ])