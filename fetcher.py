import time
import schedule

from utils import generate_time_list


class DataFetcher:
    def __init__(self, notify_callback) -> None:
        self.notify_callback = notify_callback

    def fetch_data(self):
        pass

    def check_condition(self):
        pass

    def check_and_notify(self):
        pass

    def schedule_data_check(self):
        times = generate_time_list("08:00", "18:00", 30)

        for t in times:
            schedule.every().day.at(t).do(self.check_and_notify)

        while True:
            schedule.run_pending()
            time.sleep(1)
