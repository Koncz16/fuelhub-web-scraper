import scrapy
from scrapy.selector import Selector
import json
from dotenv import load_dotenv
import os
from ..Models.station_data import Station
from ..Models.fuel_data import Fuel
from ..Enums.fuel_quality import FuelQuality
from ..Enums.fuel_type import FuelType

load_dotenv()

class RompetrolSpider(scrapy.Spider):
    name = "rompetrol"
    allowed_domains = ["rompetrol.ro"]
    start_urls = [os.getenv("ROMPETROL_API_URL")]


    def parse(self, response):
        data = json.loads(response.text)

        for station in data:
            infowindow = station.get("infowindow")
            fuels = self.extract_fuels(response, infowindow)

            yield Station(
                external_id=str(station.get("id")),
                name=station.get("name"),
                brand=station.get("brand", "Rompetrol"),
                city=station.get("city"),
                county=station.get("county"),
                address=station.get("address"),
                postal_code=station.get("postal_code", ""),
                latitude=station.get("lat"),
                longitude=station.get("lng"),
                fuels=fuels
            )

    def extract_fuels(self, response, infowindow_html):
        fuels = []

        selector = Selector(text=infowindow_html)
    
        fuel_items = selector.xpath('//div[@class="item"]')

        for item in fuel_items:
            fuel_name = item.xpath('.//div[@class="fuel"]/text()').get().strip()
            fuel_price = item.xpath('.//span[@class="small"]/text()').get().replace("LEI/L", "").strip()

            if fuel_price:
                fuel_price = float(fuel_price)

            fuel_type = self.get_fuel_type(fuel_name)
            fuel_quality = self.get_fuel_quality(fuel_name)

            fuel = Fuel(type=fuel_type, quality=fuel_quality, price=fuel_price)
            fuels.append(fuel)

        return fuels

    def get_fuel_type(self, fuel_name):
        if "Benzin" in fuel_name:
            return FuelType.BENZIN.value
        elif "Motorina" in fuel_name:
            return FuelType.MOTORINA.value
        elif "GPL" in fuel_name:
            return FuelType.GPL.value
        else:
            return FuelType.BENZIN 

    def get_fuel_quality(self, fuel_name):
        if "Efix S" in fuel_name:
            return FuelQuality.PREMIUM.value
        elif "Efix" in fuel_name:
            return FuelQuality.NORMAL.value
        else:
            return FuelQuality.NORMAL.value  