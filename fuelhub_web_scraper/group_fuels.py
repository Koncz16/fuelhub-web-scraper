import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from fuelhub_web_scraper.Models.station import FuelStation

def group_raw_file(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    stations = defaultdict(lambda: {"prices": {}, "info": {}})

    for row in raw_data:
        station_id = row["station_id"]

        # Store station info once, using the source timestamp.
        if not stations[station_id]["info"]:
            timestamp_str = row.get("timestamp")
            stations[station_id]["info"] = {
                "station_id": station_id,
                "brand": row.get("brand"),
                "city": row.get("city"),
                "county": row.get("county"),
                "address": row.get("address"),
                "latitude": None,
                "longitude": None,
                "timestamp": datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.utcnow(),
            }

        stations[station_id]["prices"][row["fuel"]] = row.get("price")

    grouped_stations = []
    for station_data in stations.values():
        station_obj = FuelStation(**station_data["info"], prices=station_data["prices"])
        grouped_stations.append(station_obj.to_dict())

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(grouped_stations, f, ensure_ascii=False, indent=2)

    return len(grouped_stations)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "grupped_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(base_dir.glob("raw_output*.json"))
    if not raw_files:
        print("No raw_output JSON files found.")
        return

    for raw_file in raw_files:
        grouped_filename = raw_file.name.replace("raw_output", "grouped_output", 1)
        output_file = output_dir / grouped_filename
        grouped_count = group_raw_file(raw_file, output_file)
        print(f"{raw_file.name} -> {output_file.name} ({grouped_count} stations)")


if __name__ == "__main__":
    main()