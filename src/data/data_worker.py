import datetime
from typing import List

import pandas as pd

from src.configuration import *
from src.enums.online_statusplatform import OnlineStatusPlatform
from src.mongo.constants import *
from src.utils import Utils


class DataWorker:
    @staticmethod
    def get_available_days_for_id(activity_csv: pd.DataFrame, follower_id: int) -> List[datetime.datetime]:
        df = activity_csv.copy()
        df = df[df[ID_KEY] == follower_id]

        df[DATETIME_KEY] = df[DATETIME_KEY].apply(Utils.get_date_truncated_by_day)
        available_date_timestamps = set((df[DATETIME_KEY].tolist()))
        available_dates = sorted(list(available_date_timestamps))
        return available_dates

    @staticmethod
    def get_online_status_string(online_status_int: int) -> str:
        if online_status_int == 0:
            return "OFFLINE"
        elif online_status_int == 1:
            return "ONLINE"
        elif online_status_int is None:
            return "UNKNOWN"
        raise ArithmeticError(f"Online status must be 0, 1 or None. Was: {online_status_int}")

    def get_one_day_df_for_id(self, activity_csv: pd.DataFrame, chosen_date: datetime.datetime, follower_id: int):
        raw_df = activity_csv.copy()

        df_for_id = raw_df
        df_for_id = df_for_id[df_for_id[ID_KEY] == follower_id]

        df_for_id_and_day = df_for_id.copy()

        df_for_id_and_day = df_for_id_and_day[df_for_id_and_day[DATETIME_KEY].apply(Utils.get_date_truncated_by_day) == chosen_date]

        filtered_df = df_for_id_and_day[[MINUTES_INTERVAL_NUMBER_KEY, ONLINE_KEY, PLATFORM_KEY]].set_index(MINUTES_INTERVAL_NUMBER_KEY)
        minutes_interval_online_dict = filtered_df.to_dict()[ONLINE_KEY]
        platform_dict = filtered_df.to_dict()[PLATFORM_KEY]

        minutes_intervals_datetimes_dict = {}
        current_datetime = chosen_date
        platforms_list = []

        no = "NO"
        for i in range(MINUTES_INTERVALS_NUMBER):

            if i in minutes_interval_online_dict:
                current_online_status = minutes_interval_online_dict[i]
            else:
                current_online_status = None
            minutes_intervals_datetimes_dict[current_datetime] = self.get_online_status_string(current_online_status)

            if i in platform_dict:
                if minutes_interval_online_dict[i] == 0:
                    platforms_list.append(no)
                else:
                    platforms_list.append(OnlineStatusPlatform(platform_dict[i]).name)
            else:
                platforms_list.append(no)
            current_datetime += datetime.timedelta(0, 0, 0, 0, MINUTES_INTERVAL)

        df = pd.Series(minutes_intervals_datetimes_dict).to_frame(ONLINE_KEY)
        df[PLATFORM_KEY] = platforms_list

        index_name = "index"

        df.index.name = index_name
        df = df.reset_index()
        df[index_name] = df[index_name].apply(lambda datetime: datetime.strftime(DATETIME_WRITE_FORMAT))
        df[index_name] = pd.to_datetime(df[index_name], format=DATETIME_WRITE_FORMAT)
        df[index_name] = df[index_name].dt.tz_localize('Europe/London')
        df[index_name] = df[index_name].dt.tz_convert('Europe/Moscow')

        return df

    @staticmethod
    def get_one_month_altair_chart_for_id(chosen_month: datetime.datetime, follower_id: int):
        print(1)


