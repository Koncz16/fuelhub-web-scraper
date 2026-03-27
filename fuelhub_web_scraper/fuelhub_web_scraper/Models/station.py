from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

@dataclass
class FuelStation:
    station_id: str
    brand: str
    city: str
    county: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    prices: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = datetime.utcnow()

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "brand": self.brand,
            "city": self.city,
            "county": self.county,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "prices": self.prices,
            "timestamp": self.timestamp.isoformat()
        }