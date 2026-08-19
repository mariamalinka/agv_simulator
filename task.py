from dataclasses import dataclass


@dataclass
class Task:
    id: int
    pickup: tuple[int, int]
    delivery: tuple[int, int]
    status: str = "waiting"


    created_at: int = 0
    assigned_at: int | None = None
    picked_up_at: int | None = None
    completed_at: int | None = None
