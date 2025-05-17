import os
import scrapy
import json
from dotenv import load_dotenv
import re
from ..Models.station_data import Station
from ..Models.fuel_data import Fuel
from ..Enums.fuel_quality import FuelQuality
from ..Enums.fuel_type import FuelType

load_dotenv() 

class MolSpider(scrapy.Spider):
    name = "mol"
    allowed_domains = ["cautarestatii.molromania.ro"]
    start_urls = [os.getenv("MOL_API_URL")]

    def start_requests(self):
        payload = {
            "api": os.getenv("MOL_API"),
            "mode": os.getenv("MOL_MODE"),
            "lang": os.getenv("MOL_LANG"),
            "input": os.getenv("MOL_INPUT"),
        }
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://cautarestatii.molromania.ro",
            "Referer": "https://cautarestatii.molromania.ro/"
        }
        yield scrapy.Request(
            url=self.start_urls[0],
            method="POST",
            body=json.dumps(payload),
            headers=headers,
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.text)
        stations = data if isinstance(data, list) else [data]

        for station in stations:
            external_id = str(station.get("code", ""))
            name = station.get("name", "")
            brand = station.get("brand", "MOL")
            city = self.extract_city_from_name(name)

            county = ""
            county_values = station.get("county", {}).get("values", [])
            if county_values:
                county = county_values[0].get("name", "")

            address = station.get("address", "")
            postal_code = station.get("postcode", "")
            gps = station.get("gpsPosition", {})
            latitude = gps.get("latitude")
            longitude = gps.get("longitude")

            fuels = self.extract_fuels(station)

            yield Station(
                external_id=external_id,
                name=name,
                brand=brand,
                city=city,
                county=county,
                address=address,
                postal_code=postal_code,
                latitude=latitude,
                longitude=longitude,
                fuels=fuels
            )

    def extract_fuels(self, station):
        fuels = []
        for fuel in station.get("fuelsAndAdditives", {}).get("values", []):
            fuel_name = fuel.get("name", "")
            fuel_type = self.get_fuel_type(fuel_name)
            fuel_quality = self.get_fuel_quality(fuel_name)
            fuels.append(Fuel(type=fuel_type, quality=fuel_quality, price=None))
        return fuels

    def get_fuel_type(self, fuel_name):
        name = fuel_name.lower()
        if "benzin" in name or "evo 95" in name or "evo 100" in name:
            return FuelType.BENZIN.value
        if "diesel" in name:
            return FuelType.MOTORINA.value
        if "gpl" in name:
            return FuelType.GPL.value
        return FuelType.BENZIN.value

    def get_fuel_quality(self, fuel_name):
        name = fuel_name.lower()
        if "plus" in name or "100" in name:
            return FuelQuality.PREMIUM.value
        return FuelQuality.NORMAL.value

    def extract_city_from_name(self, name):
        if " - " in name:
            before_dash = name.split(" - ")[0].strip()
            return re.sub(r"\s+\d+$", "", before_dash)
        else:
            return re.sub(r"\s+\d+$", "", name.strip())