from dataclasses import dataclass
from typing import List
from .fuel_data import Fuel

@dataclass
class Station:
    external_id: str
    name: str
    brand: str
    city: str
    county: str
    address: str
    postal_code: str
    latitude: float
    longitude: float
    fuels: List[Fuel] = None 
