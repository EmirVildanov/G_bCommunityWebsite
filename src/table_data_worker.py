import datetime
from io import StringIO
from typing import List

import pandas as pd

from src.configuration import *
from src.mongo.constants import *
from src.utils import Utils


class TableDataWorker:
    @staticmethod
    def get_available_days_for_id(activity_csv: pd.DataFrame, follower_id: int) -> List[datetime.datetime]:
        df = activity_csv.copy()
        df = df[df[ID_KEY] == follower_id]

        def get_truncated_date(string) -> datetime:
            try:
                return Utils.get_date_truncated_from_string(string,
                                                            DATETIME_STANDARD_FORMAT)
            except ValueError:
                return Utils.get_date_truncated_from_string(string,
                                                            DATETIME_STANDARD_FORMAT_WITHOUT_MILLISECONDS)

        df[DATETIME_KEY] = df[DATETIME_KEY].apply(get_truncated_date)
        available_date_timestamps = set((df[DATETIME_KEY].tolist()))
        available_dates = [Utils.get_date_truncated(datetime) for datetime in list(available_date_timestamps)]
        return available_dates
