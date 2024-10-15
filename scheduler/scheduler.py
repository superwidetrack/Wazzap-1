import schedule
import time

class Scheduler:
    def __init__(self):
        self.schedule = schedule

    def set_night_mode(self, start_time, end_time):
        # Настройка ночного режима
        pass

    def run(self):
        while True:
            self.schedule.run_pending()
            time.sleep(1)
