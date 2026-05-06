import scrapy
from collections import defaultdict
import hashlib
from datetime import datetime
from fuelhub_web_scraper.Models.station import FuelStation


class PecoSpider(scrapy.Spider):
    name = "peco"

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    base_url = "https://peco-online.ro/index.php"

    fuels = {
        "benzina": "Benzina_Regular",
        "diesel": "Motorina_Regular",
        "gpl": "GPL",
        "benzina_extra": "Benzina_Premium",
        "diesel_extra": "Motorina_Premium"
    }

    counties = ["Cluj", "Alba", "Arad", "Arges", "Bacau", "Bihor", "Bistrita", 
    "Botosani", "Brasov", "Braila", "Bucuresti", "Buzau", "Caras-Severin", 
     "Calarasi", "Cluj", "Constanta", "Covasna", "Dambovita", "Dolj", 
     "Galati", "Giurgiu", "Gorj", "Harghita", "Hunedoara", "Ialomita", 
      "Iasi", "Ilfov", "Maramures", "Mehedinti", "Mures", "Neamt", 
       "Olt", "Prahova", "Satu Mare", "Salaj", "Sibiu", "Suceava", 
        "Teleorman", "Timis", "Tulcea", "Vaslui", "Valcea", "Vrancea" ]

    # counties = ["Mures"]  # start with one county, extend later

    retele = [
        "Gazprom", "Lukoil", "Mol", "OMV", "Petrom", "Rompetrol",
        "Socar", "ALD", "BLKOil", "CellyRo", "DHR", "Metropoli",
        "Ozana", "Petrolium", "Petromar", "RST", "TEAutohof", "VhExtraOil"
    ]

    def start_requests(self):
        for fuel_name, fuel_value in self.fuels.items():
            for county in self.counties:
                yield scrapy.FormRequest(
                    url=self.base_url,
                    formdata=self.build_formdata(fuel_value, county),
                    callback=self.parse,
                    meta={
                        "fuel": fuel_name,
                        "county": county
                    }
                )

    def build_formdata(self, fuel, county):
        data = {
            "carburant": fuel,
            "locatie": "Judet",
            "nume_locatie": county
        }
        data["retele[]"] = self.retele
        return data

    def parse(self, response):
        fuel = response.meta["fuel"]
        county = response.meta["county"]

        for station in response.css("div.rezultat"):
            brand = station.css("img::attr(alt)").get()
            spans = [s.strip() for s in station.css("div.flex-grow-1 span::text").getall() if s.strip()]
            station_name = spans[0] if len(spans) > 0 else None
            city = spans[1] if len(spans) > 1 else None
            address = station.css("span.text-muted::text").get()
            price = station.css("h3.pret strong::text").get()

            station_id = hashlib.md5(f"{brand}-{city}-{address}".encode()).hexdigest()

            # Yield
            yield {
                "station_id": station_id,
                "fuel": fuel,
                "county": county,
                "brand": brand,
                "station_name": station_name,
                "city": city,
                "address": address.strip() if address else None,
                "price": float(price) if price else None,
                "timestamp": datetime.utcnow().isoformat()
            }