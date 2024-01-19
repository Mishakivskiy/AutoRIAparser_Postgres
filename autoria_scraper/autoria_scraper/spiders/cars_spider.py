import scrapy
import re
import requests
from bs4 import BeautifulSoup
from .db import insert_data_into_postgres


class CarsSpider(scrapy.Spider):
    name = 'cars'
    start_urls = ['https://auto.ria.com/uk/car/used/?page=1']

    def parse(self, response):
        for cars in response.css('div.content-bar'):
            car_url = cars.css('a.m-link-ticket').attrib['href']
            yield scrapy.Request(car_url, callback=self.parse_car_details)

        next_page = response.css('a.page-link.js-next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_car_details(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', class_=re.compile(r'js-user-secure-\d+'))
        data_hash = script_tag['data-hash']
        data_expires = script_tag['data-expires']
        data_advertisement_id = re.search(r'(\d+)\.html$', response.url).group(1)

        base_url = "https://auto.ria.com/users/phones/"
        url = f"{base_url}{data_advertisement_id}?hash={data_hash}&expires={data_expires}"
        phone_response = requests.get(url)
        if phone_response.status_code == 200:
            json_data = phone_response.json()
            formatted_phone_number = json_data.get('formattedPhoneNumber')
            digits = ''.join(filter(str.isdigit, formatted_phone_number))
            international_format = '+38' + digits

        car_details = {
            'url': response.url,
            'title': response.css('h1.head::text').get(),
            'price_usd': int(response.css('div.price_value strong::text').get().replace('$', '').replace(' ', '')),
            'odometer': int(response.css('div.base-information.bold span.size18::text').get() + '000'),
            'username': response.css('div.seller_info_name.bold::text').get() if response.css('div.seller_info_name.bold::text').get() != None else response.css('h4.seller_info_name a::text').get(),
            'phone_number': international_format,
            'image_url': response.css('img.outline.m-auto').attrib['src'],
            'images_count': int(re.sub(r'\D', '', response.css('a.show-all.link-dotted::text').get())),
            'car_number': response.css('span.state-num::text').get() or None,
            'car_vin': response.css('span.label-vin::text').get() or response.css('span.vin-code::text').get(),
        }

        insert_data_into_postgres(car_details)
