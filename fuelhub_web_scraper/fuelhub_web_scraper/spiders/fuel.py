import scrapy


class FuelSpider(scrapy.Spider):
    name = "fuel"
    allowed_domains = ["www.peco-online.ro"]
    start_urls = ["https://www.peco-online.ro/index.php"]

    def parse(self, response):
        # rows = response.xpath('//tr[td[@class="lead text-center align-middle"]]')
        rows = response.xpath('//tr[td/span[@class="pret font-weight-bold"]]')


        for row in rows:
            yield {
                'price': row.xpath('.//span[@class="pret font-weight-bold"]/text()').get(),
                'type': row.xpath('.//img/@alt').get(),  # pl. "Petrolium"
                'location': row.xpath('.//span[@class="small d-block text-muted"]/text()').get(),
                'address': row.xpath('.//span[not(@class)]/text()').get()
            }