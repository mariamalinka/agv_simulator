from main import main


ROBOT_COUNTS = [
    1,
    2,
    3,
    4,
    5,
    6,
]

RANDOM_SEEDS = [
    1,
    2,
    3,
    4,
    5,
]


for robot_count in ROBOT_COUNTS:

    for seed in RANDOM_SEEDS:

        print(
            f"Experiment: "
            f"{robot_count} robots, "
            f"seed {seed}"
        )

        main(
            number_of_robots=robot_count,
            random_seed=seed,
            visual=False,
        )