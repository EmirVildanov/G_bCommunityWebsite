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
        "<h4 style='text-align: center;'>In order to obtain your account info send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h5 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_FOR_ACCOUNT_INFO}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h4 style='text-align: center;'>message to G_b group messages</h1>",
        unsafe_allow_html=True)


def write_secret_key_bot_communication_info():
    st.markdown(
        "<h4 style='text-align: center;'>To see your online activity you have to receive private security key</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h4 style='text-align: center;'>In order to do it send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h5 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_FOR_PASSWORD}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h4 style='text-align: center;'>message to G_b group messages</h1>",
        unsafe_allow_html=True)


def write_change_publicity_status_bot_communication_info():
    st.markdown(
        "<h4 style='text-align: center;'>In order to change your account publicity status send</h1>",
        unsafe_allow_html=True)

    st.markdown(
        f"<h5 style='text-align: center; color: green'>{SECRET_MESSAGE_LINE_ASKING_TO_CHANGE_PUBLIC_STATUS}</h1>",
        unsafe_allow_html=True)

    st.markdown(
        "<h4 style='text-align: center;'>message to G_b group messages</h1>",
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

    st.title("[G_b](https://vk.com/gebum) followers activity tracker")
    st.write("(data loading can take a lot of time, yeah)")

    st.write("**Public accounts**. Data about public accounts is public and can be viewed by anyone.")
    st.write("**Private accounts**. "
             "Data about private accounts is hidden and can only be viewed by users who have the secret key.")
    st.write("**You can always change whether your account is private or public on this website**")
    st.text("")
    st.text("")

    pretty_publicity_options = {choice.name: choice for choice in PublicityChoice}
    publicity_option = st.selectbox(
        "Choose the information type you want to get:",
        pretty_publicity_options.keys()
    )

    follower_id = -1

    if pretty_publicity_options[publicity_option] == PublicityChoice.PUBLIC:
        st.write("Here you can only discover users who marked their accounts as public.")
        st.text("")

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
        st.write("Here you can view data about your account without making it public.")
        st.write("To do this you must obtain a secret key.")
        st.text("")

        account_info = st.text_input("Enter your surname:")

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

        date = st.date_input(
            "Choose the date",
            value=available_dates[len(available_dates) - 1],
            min_value=available_dates[0],
            max_value=available_dates[len(available_dates) - 1]
        )

        df = data_worker.get_one_day_df_for_id(activity_csv, date,
                                               follower_id)
        fig = px.scatter(df, x="index", y="online", color="platform", symbol="platform",
                         labels={
                             "index": "time",
                             "online": "online_status",
                         },
                         category_orders={"online": ["ONLINE", "OFFLINE", "UNKNOWN"],
                                          "platform": ["MOBILE", "ANDROID", "IPHONE", "WEB", "NO"]})
        st.plotly_chart(fig, use_container_width=True)

    st.text("")
    st.write("Check out github repo [link](https://github.com/EmirVildanov/G_bCommunityWebsite) !")
