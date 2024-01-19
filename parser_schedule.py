import schedule
import time
import pytz
import subprocess
from datetime import datetime, timedelta
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from autoria_scraper.autoria_scraper.spiders.cars_spider import CarsSpider

def run_parser():
    process = CrawlerProcess(get_project_settings())
    process.crawl(CarsSpider)
    process.start()

def dump_database():
    dump_filename = f"dumps/db_dump_{datetime.now().strftime('%Y%m%d%H%M%S')}.sql"
    command = f"pg_dump -h localhost -U your_username -d your_database_name -f {dump_filename}"
    subprocess.run(command, shell=True)

utc_now = datetime.now(pytz.utc)

schedule_time = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)

if utc_now > schedule_time:
    schedule_time += timedelta(days=1)

schedule.every().day.at(schedule_time.strftime("%H:%M")).do(dump_database)
schedule.every().day.at(schedule_time.strftime("%H:%M")).do(run_parser)

while True:
    schedule.run_pending()
    time.sleep(1)
