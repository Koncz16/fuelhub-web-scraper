from dataclasses import dataclass
from typing import List
from .FuelData import Fuel

@dataclass
class Station:
    id: int
    name: str
    brand: str
    city: str
    county: str
    address: str
    postal_code: str
    latitude: float
    longitude: float
    fuels: List[Fuel] = None 
