"""
Author: bishwarup
Created: Friday, 17th March 2020 3:24:31 pm
Modified: Friday, 20th March 2020 2:42:57 pm [bishwarup]
"""
from bs4 import BeautifulSoup
import requests
from fetch import get_record, format_records
from datetime import datetime, timedelta
import time
import json
import argparse


class Update:
    def __init__(self, url):
        self.url = url
        self._total_cases = 168
        self._last_updated = datetime.now()

    @property
    def total_cases(self):
        return self._total_cases

    @total_cases.setter
    def total_cases(self, value):
        if value > self.total_cases:
            self._total_cases = value

    @property
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        if isinstance(value, datetime):
            self._last_updated = value

    def _needs_update(self):
        with open("overall.json", "r") as f:
            overall = json.load(f)
        last_updated = datetime.strptime(overall["timestamp"], "%d/%m/%Y %H-%M-%S")
        del overall["timestamp"]
        latest = self.get_overall()

        if (latest != sum(overall.values())) or (
            (datetime.now() - last_updated).days > 1
        ):
            latest["timestamp"] = datetime.strftime(datetime.now(), "%d/%m/%Y %H-%M-%S")
            with open("overall.json", "w") as f:
                json.dump(latest, f)
            return True

    def get_overall(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"{datetime.now()} : Server unresponsive!")
        text = response.text
        soup = BeautifulSoup(text, "lxml")
        table = soup.find(text="S. No.").find_parent("table")
        rows = table.find_all("tr")
        sums = [col.get_text().replace("\n", "") for col in rows[-1].find_all("td")][1:]
        return {
            "Confirmed": int(sums[0]) + int(sums[1]),
            "Recovered": int(sums[2]),
            "Death": int(sums[3]),
        }

    # def _check_for_update(self):
    #     response = requests.get(self.url)
    #     if response.status_code != 200:
    #         print(f"{datetime.now()} : Server unresponsive!")
    #     text = response.text
    #     soup = BeautifulSoup(text, "lxml")
    #     table = soup.find(text="S. No.").find_parent("table")
    #     rows = table.find_all("tr")
    #     sums = [col.get_text().replace("\n", "") for col in rows[-1].find_all("td")][1:]
    #     return sum([int(x) for x in sums])

    def update(self, history):
        if self._needs_update():
            record = get_record(self.url)
            record = format_records(
                datetime.strftime(datetime.now(), "%d/%m/%Y"), record
            )
            for k, v in record.items():
                if k in history.keys():
                    history[k].update(record[k])
                else:
                    history[k] = record[k]
        with open("history.json", "w") as f:
            json.dump(history, f)
        print("{} : updated".format(datetime.now().strftime("%d/%m/%Y %H-%M-%S")))
        return history

    # def run(self, waiting=60):
    #     while True:
    #         total_cases = self._check_for_update()
    #         if total_cases > self.total_cases:
    #             self._update()
    #             self.last_updated = datetime.now()
    #             self.total_cases = total_cases
    #         else:
    #             print(
    #                 "{}: records not updated yet, will check again in {:.2f} hr.".format(
    #                     datetime.now().strftime("%d/%m/%Y %H-%M-%S"), waiting / 3600
    #                 )
    #             )
    #         time.sleep(waiting)


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "-t",
    #     "--waiting",
    #     type=int,
    #     default=60,
    #     help="waiting time for the next check (in seconds)",
    # )
    # args = vars(parser.parse_args())
    update = Update("https://www.mohfw.gov.in/")
    overall = update.get_overall()
    overall["timestamp"] = (datetime.now() - timedelta(days=3)).strftime(
        "%d/%m/%Y %H-%M-%S"
    )
    with open("overall.json", "w") as f:
        json.dump(overall, f)
    # update.run(args["waiting"])
