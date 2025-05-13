from dataclasses import dataclass
from ..Enums.FuelQuality import FuelQuality
from ..Enums.FuelType import FuelType

@dataclass
class Fuel:
    type: str          
    quality: str  
    price: float            
