from pydantic import BaseModel
from typing import List, Optional


class State(BaseModel):
    agent_position: List[int]
    inventory: List[str]
    current_order: Optional[List[str]]
    orders_completed: int
    time: int
    battery: int


class Action(BaseModel):
    action: str
