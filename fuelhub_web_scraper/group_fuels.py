import json
from collections import defaultdict
from datetime import datetime
from fuelhub_web_scraper.Models.station import FuelStation

# Load the raw output
with open("raw_output.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Temporary storage to group fuels per station
stations = defaultdict(lambda: {"prices": {}, "info": {}})

for row in raw_data:
    station_id = row["station_id"]
    
    # Store station info once
    if not stations[station_id]["info"]:
        stations[station_id]["info"] = {
            "station_id": station_id,
            "brand": row.get("brand"),
            "city": row.get("city"),
            "county": row.get("county"),
            "address": row.get("address"),
            "latitude": None,    
            "longitude": None,
            "timestamp": datetime.utcnow()
        }
    
    # Add fuel price
    stations[station_id]["prices"][row["fuel"]] = row.get("price")

# Create final grouped list
grouped_stations = []
for s in stations.values():
    station_obj = FuelStation(**s["info"], prices=s["prices"])
    grouped_stations.append(station_obj.to_dict())

# Save grouped JSON
with open("grouped_output.json", "w", encoding="utf-8") as f:
    json.dump(grouped_stations, f, ensure_ascii=False, indent=2)

print(f"Grouped {len(grouped_stations)} stations with all fuels.")