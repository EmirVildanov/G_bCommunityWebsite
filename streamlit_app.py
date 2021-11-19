import pandas as pd
import streamlit as st
import plotly.express as px
import datetime

from src.configuration import *
from src.data.data_worker import DataWorker
from src.mongo.constants import ID_KEY, DATETIME_KEY
from src.mongo.mongo_worker import MongoWorker
from src.sreamlit.publicity_choice import PublicityChoice
from src.vk.constants import *
from src.vk.vk_worker import VkWorker


def write_account_info_bot_communication_info():
    st.markdown(
        "<h3 style='text-align: center;'>In order to obtain your account info send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h4 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_FOR_ACCOUNT_INFO}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: center;'>message to G_b group messages</h1>",
        unsafe_allow_html=True)


def write_secret_key_bot_communication_info():
    st.markdown(
        "<h3 style='text-align: center;'>To see your online activity you have to receive private security key</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: center;'>In order to do it send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h4 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_FOR_PASSWORD}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: center;'>message to G_b group messages</h1>",
        unsafe_allow_html=True)


def write_change_publicity_status_bot_communication_info():
    st.markdown(
        "<h3 style='text-align: center;'>In order to change your account publicity status send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h4 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_TO_CHANGE_PUBLIC_STATUS}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: center;'>message to G_b group messages</h1>",
        unsafe_allow_html=True)


def write_error(message: str):
    st.markdown(
        f"<h4 style='text-align: left; color: red'>{message}</h1>",
        unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    data_worker = DataWorker()
    vk_worker = VkWorker(GROUP_ACCESS_TOKEN)
    mongo_worker = MongoWorker()

    hide_streamlit_settings_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer
    {visibility: hidden;}
    </style>

    """
    st.markdown(hide_streamlit_settings_style, unsafe_allow_html=True)

    st.title("G_b followers activity tracker")
    st.write("(data loading can take a lot of time, yeah)")

    pretty_publicity_options = {choice.name: choice for choice in PublicityChoice}
    publicity_option = st.selectbox(
        "Choose the information type you want to get:",
        pretty_publicity_options.keys()
    )

    follower_id = -1

    if pretty_publicity_options[publicity_option] == PublicityChoice.PUBLIC:

        public_accounts = mongo_worker.get_public_followers_info()
        if len(public_accounts) != 0:
            pretty_account_options = {f"{account.name} {account.surname} ({account.id})": account for
                                      account in public_accounts}
            account_option = st.selectbox(
                "Choose the person, whose activity info you want to get:",
                pretty_account_options.keys()
            )
            chosen_account = pretty_account_options[account_option]
            follower_id = chosen_account.id
        else:
            write_error("There is no public account")
        write_change_publicity_status_bot_communication_info()
    else:
        account_info = st.text_input("Enter your surname:")

        # if account_info != "" and account_info.isnumeric() and int(account_info) > 0 and mongo_worker.is_id_exists(account_info):
        #     if mongo_worker.is_account_with_id_is_public(id):
        #         st.write("Your account is public")
        if account_info != "" and mongo_worker.is_surname_exists(account_info):
            write_secret_key_bot_communication_info()

            secret_key = st.text_input("Your secret key")

            if mongo_worker.is_surname_fits_with_secret_key(account_info, secret_key):
                follower_id = mongo_worker.get_user_id_by_secret_key(secret_key)[ID_KEY]
            elif secret_key != "":
                write_error("Key is wrong, so I can't show you the info")
        elif account_info != "":
            write_error("There is no account with such surname")
            write_account_info_bot_communication_info()

    if follower_id != -1:
        activity_data = mongo_worker.get_activity_info_csv()
        activity_csv = pd.read_csv(activity_data, sep=",")
        activity_csv[DATETIME_KEY] = pd.to_datetime(activity_csv[DATETIME_KEY])

        available_dates = DataWorker.get_available_days_for_id(activity_csv, follower_id)
        pretty_available_datetime_pairs = {datetime.datetime.strftime(date, DATETIME_ONLY_DATE_FORMAT): date for
                                           date in available_dates}

        date_option = st.selectbox(
            "Choose the date",
            pretty_available_datetime_pairs.keys()
        )

        df = data_worker.get_one_day_df_for_id(activity_csv, pretty_available_datetime_pairs[date_option],
                                               follower_id)
        fig = px.scatter(df, x="index", y="online", color="platform", symbol="platform",
                         category_orders={"online": ["ONLINE", "OFFLINE", "UNKNOWN"],
                                          "platform": ["MOBILE", "WEB", "NO"]})
        st.plotly_chart(fig, use_container_width=True)
