import datetime
from io import StringIO

import pandas as pd
import altair as alt

from src.configuration import *
from src.mongo.constants import *
from src.utils import Utils


class GraphDataWorker:
    @staticmethod
    def get_one_day_altair_chart_for_id(activity_csv: pd.DataFrame, chosen_day_string: str, follower_id: int):
        chosen_day = datetime.datetime.strptime(chosen_day_string, DATETIME_SAVE_FILE_NAME_FORMAT)
        raw_df = activity_csv.copy()

        df_for_id = raw_df
        df_for_id = df_for_id[df_for_id[ID_KEY] == follower_id]

        df_for_id_and_day = df_for_id.copy()

        def get_truncated_date(string) -> datetime:
            try:
                return Utils.get_date_truncated_from_string(string,
                                                            DATETIME_STANDARD_FORMAT)
            except ValueError:
                return Utils.get_date_truncated_from_string(string,
                                                            DATETIME_STANDARD_FORMAT_WITHOUT_MILLISECONDS)

        df_for_id_and_day[DATETIME_KEY] = df_for_id_and_day[DATETIME_KEY].apply(get_truncated_date)
        df_for_id_and_day = df_for_id_and_day[df_for_id_and_day[DATETIME_KEY] == pd.Timestamp(chosen_day)]

        filtered_df = df_for_id_and_day[[MINUTES_INTERVAL_NUMBER_KEY, ONLINE_KEY, PLATFORM_KEY]].set_index(MINUTES_INTERVAL_NUMBER_KEY)
        minutes_interval_online_dict = filtered_df.to_dict()[ONLINE_KEY]
        platform_dict = filtered_df.to_dict()[PLATFORM_KEY]

        minutes_intervals_datetimes_dict = {}
        current_datetime = datetime.datetime.min
        # platforms_dict = []
        platforms_list = []

        for i in range(MINUTES_INTERVALS_NUMBER):
            if i in minutes_interval_online_dict:
                minutes_intervals_datetimes_dict[current_datetime] = minutes_interval_online_dict[i]
            else:
                minutes_intervals_datetimes_dict[current_datetime] = None

            if i in platform_dict:
                # platforms_dict[current_datetime] = platform_dict[i]
                platforms_list.append(platform_dict[i])
            else:
                # platforms_dict[current_datetime] = None
                platforms_list.append(None)
            current_datetime += datetime.timedelta(0, 0, 0, 0, MINUTES_INTERVAL)

        df = pd.Series(minutes_intervals_datetimes_dict).to_frame(ONLINE_KEY)

        test_df = df.copy()
        test_df[PLATFORM_KEY] = df_for_id_and_day[PLATFORM_KEY]
        df[PLATFORM_KEY] = platforms_list

        index_name = "index"

        df.index.name = index_name
        df = df.reset_index()
        df[index_name] = df[index_name].apply(lambda datetime: datetime.strftime(DATETIME_TIME_INTERVAL_NAME_FORMAT))
        df[index_name] = pd.to_datetime(df[index_name], format=DATETIME_TIME_INTERVAL_NAME_FORMAT)
        df[index_name] = df[index_name].dt.tz_localize('Europe/Moscow')

        # selection = alt.selection_multi(fields=[PLATFORM_KEY], bind="legend")

        hover = alt.selection(
            type="single", on="mouseover", fields=[index_name], nearest=True
        )

        chart = alt.Chart(df).mark_circle().encode(
            alt.X(f'hoursminutes({index_name}):O', title='day time'),
            alt.Y(f'{ONLINE_KEY}:N', sort="descending"),
            color=alt.Color(f'{PLATFORM_KEY}:N'),
            # opacity=alt.condition(selection, alt.value(1), alt.value(0.1))
        ).properties(
            title=f"User online activity on {chosen_day.strftime(DATETIME_SAVE_FILE_NAME_FORMAT)}",
            width=800,
            height=800
        )

        point = chart.mark_circle().encode(
            opacity=alt.value(0)
        ).add_selection(hover)

        singleline = chart.mark_line().encode(
            size=alt.condition(~hover, alt.value(0.5), alt.value(3))
        )

        return chart, df, test_df, df_for_id_and_day

    @staticmethod
    def get_one_month_altair_chart_for_id(chosen_month: datetime.datetime, follower_id: int):
        print(1)

