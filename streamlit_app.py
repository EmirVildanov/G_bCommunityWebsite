import pandas as pd
import streamlit as st

from src.configuration import *
from src.graph_data_worker import GraphDataWorker
from src.mongo.constants import ID_KEY, MONGODB_PASSWORD_KEY, MONGODB_USERNAME_KEY
from src.mongo.mongo_worker import MongoWorker
from src.table_data_worker import TableDataWorker
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


def write_error(message: str):
    st.markdown(
        f"<h4 style='text-align: left; color: red'>{message}</h1>",
        unsafe_allow_html=True)


if __name__ == "__main__":
    os.environ[MONGODB_PASSWORD_KEY] = "wsDqfAlAfTNAUf1n"
    os.environ[MONGODB_USERNAME_KEY] = "GeneralBum"

    st.set_page_config(layout="wide")
    graph_worker = GraphDataWorker()
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

    st.title('Vk user activity tracker')

    st.write("Emir's secret key: frise_bichon_848")

    account_info = st.text_input("Enter your surname (In English) or id (If you've already used visited this website):")

    if account_info != "" and account_info.isnumeric() and int(account_info) > 0 and mongo_worker.is_id_exists(account_info):
        if mongo_worker.is_account_with_id_is_public(id):
            print(1)
    if account_info != "" and mongo_worker.is_surname_exists(account_info):
        write_secret_key_bot_communication_info()

        secret_key = st.text_input("Your secret key")

        if mongo_worker.is_surname_fits_with_secret_key(account_info, secret_key):
            follower_id = mongo_worker.get_user_id_by_secret_key(secret_key)[ID_KEY]
            activity_data = mongo_worker.get_activity_info_csv()
            activity_csv = pd.read_csv(activity_data, sep=",")

            available_datetimes = TableDataWorker.get_available_days_for_id(activity_csv, follower_id)
            pretty_available_datetimes = [datetime.strftime(DATETIME_SAVE_FILE_NAME_FORMAT) for datetime in
                                          available_datetimes]

            option = st.selectbox(
                "Choose the date",
                pretty_available_datetimes
            )
            f"Chosen date: {option}"

            chart, df, test_df, raw_df = graph_worker.get_one_day_altair_chart_for_id(activity_csv, option, follower_id)
            st.altair_chart(chart, use_container_width=True)

            st.write(raw_df)
            st.write(test_df)
            st.write(df)

            st.write(raw_df.shape)
            st.write(test_df.shape)
            st.write(df.shape)
        elif secret_key != "":
            write_error("Key is wrong, so I can't show you the info")
    elif account_info != "":
        write_error("There is no account with such surname")
        write_account_info_bot_communication_info()