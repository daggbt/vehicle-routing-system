from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime

@dataclass
class Customer:
    id: int
    location: Tuple[float, float]
    demand: float
    time_windows: List[Tuple[datetime, datetime]]
    priority: int = 1
    
    def __str__(self):
        return f"Customer {self.id} (Priority: {self.priority}, Demand: {self.demand})"

@dataclass
class Vehicle:
    id: int
    capacity: float
    start_location: Tuple[float, float]
    route: List[Customer] = None
    schedule: List[datetime] = None
    
    def __post_init__(self):
        self.route = self.route or []
        self.schedule = self.schedule or []
    
    def __str__(self):
        return f"Vehicle {self.id} (Capacity: {self.capacity})"