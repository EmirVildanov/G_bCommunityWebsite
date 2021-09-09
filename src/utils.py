import datetime
import requests


class Utils:
    @staticmethod
    def get_date_truncated(date: datetime) -> datetime:
        return datetime.datetime(date.year, date.month, date.day)

    @staticmethod
    def get_date_truncated_from_string(date_string: str, format: str) -> datetime.datetime:
        return Utils.get_date_truncated(Utils.get_datetime_from_string(date_string, format))

    @staticmethod
    def get_datetime_from_string(date_string: str, format: str) -> datetime.datetime:
        return datetime.datetime.strptime(date_string, format)

    @staticmethod
    def log_info(info):
        print(info)

    @staticmethod
    def count_words_at_url(url):
        resp = requests.get(url)
        return len(resp.text.split())
