import scrapy
import re

class FuelSpider(scrapy.Spider):
    name = "fuel"
    allowed_domains = ["www.peco-online.ro"]
    start_urls = ["https://www.peco-online.ro/index.php"]


    def parse(self, response):
        rows = response.xpath('//tr[td/span[@class="pret font-weight-bold"]]')


        for row in rows:
            price = row.xpath('.//span[@class="pret font-weight-bold"]/text()').get()
            fuel_type = row.xpath('.//img/@alt').get()
            location = row.xpath('.//span[@class="small d-block text-muted"]/text()').get()
            address_raw = row.xpath('.//span[not(@class)]/text()').get()

            if location and ',' in location:
                city, county = [part.strip() for part in location.split(',', 1)]
            else:
                city = location.strip() if location else ''
                county = ''

            address = address_raw.strip() if address_raw else ''
            postal_code = ''

            match = re.search(r',\s*(\d{6})$', address)
            if match:
                postal_code = match.group(1)
                address = address[:match.start()].strip().rstrip(',')

            yield {
                'price': price,
                'fuel_type': fuel_type,
                'city': city,
                'county': county,
                'address': address,
                'postal_code': postal_code
            }