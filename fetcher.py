import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scraper import LANG_LEVELS_WHITELIST, fetch_seats_by_language_level, write_data_to_db


class DataFetcher:
    def __init__(self, interval) -> None:
        self.interval = interval
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def fetch_data(self):

        fetched_data = fetch_seats_by_language_level(LANG_LEVELS_WHITELIST)
        write_data_to_db(fetched_data)

    def schedule_data_fetch(self):
        self.scheduler.add_job(
            self.fetch_data,
            trigger=IntervalTrigger(seconds=self.interval),
        )

        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()


def start_fetcher():
    fetch_interval = os.getenv('FETCH_INTERVAL')

    if fetch_interval:
        print('Starting the fetcher...')
        fetcher = DataFetcher(int(fetch_interval))
        fetcher.schedule_data_fetch()


if __name__ == "__main__":
    start_fetcher()
