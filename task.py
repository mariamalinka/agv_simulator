from dataclasses import dataclass


@dataclass
class Task:
    id: int
    pickup: tuple[int, int]
    delivery: tuple[int, int]
    status: str = "waiting"
