import os
import time
import json
import scrapy
from scrapy import FormRequest
from dotenv import load_dotenv
from ..Models.station_data import Station

load_dotenv()


class PetromSpider(scrapy.Spider):
    name = "petrom"
    allowed_domains = ["app.wigeogis.com"]
    start_urls = [os.getenv("PETROM_API_URL")]

    def start_requests(self):
        ts = str(int(time.time()))
        formdata = {
            "CTRISO": os.getenv("PETROM_CTRISO"),
            "BRAND": os.getenv("PETROM_BRAND"),
            "VEHICLE": os.getenv("PETROM_VEHICLE"),
            "MODE": os.getenv("PETROM_MODE"),
            "ANZ": os.getenv("PETROM_ANZ"),
            "TS": ts,
            "HASH": os.getenv("PETROM_HASH")
        }

        yield FormRequest(
            url=self.start_urls[0],
            method="POST",
            formdata=formdata,
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.text)
        for entry in data:
            yield Station(
                external_id=entry.get("sid"),
                name=entry.get("name_l") or entry.get("brand_id"),
                brand=entry.get("brand_id"),
                city=entry.get("town_l"),
                county=entry.get("country_l"),
                address=entry.get("address_l"),
                postal_code=entry.get("postcode"),
                latitude=float(entry.get("y")),
                longitude=float(entry.get("x")),
                fuels=[]
            )

