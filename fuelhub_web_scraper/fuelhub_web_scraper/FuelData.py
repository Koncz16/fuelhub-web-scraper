from dataclasses import dataclass

@dataclass
class FuelData:
    price: str
    fuel_type: str
    city: str
    county: str
    address: str
