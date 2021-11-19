import os
from io import StringIO
from typing import List

import pymongo

from src.configuration import GROUP_ACCESS_TOKEN
from src.mongo.constants import *
from src.utils import Utils
from src.vk.vk_worker import VkWorker, FollowerInfo, PrivateFollowerInfo


class MongoWorker:
    def __init__(self):
        self.vk_worker = VkWorker(GROUP_ACCESS_TOKEN)

        mongodb_login = os.environ.get(MONGODB_USERNAME_KEY, None)
        if mongodb_login is None:
            raise RuntimeError(f"Can't read environment MONGODB_USERNAME_KEY variable")
        mongodb_password = os.environ.get(MONGODB_PASSWORD_KEY, None)
        if mongodb_password is None:
            raise RuntimeError("Can't read environment MONGODB_PASSWORD variable")

        connection_url = f"mongodb+srv://{mongodb_login}:{mongodb_password}@cluster0.bhjda.mongodb.net/Cluster0?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(connection_url)
        self.db = self.client.activity_tracker
        self.accounts = self.db.accounts
        self.activity_data = self.db.activity_data

    def insert_followers_info(self, followers_info: List[FollowerInfo]):
        already_existed_accounts = list(self.accounts.find())
        already_existed_ids = [item["id"] for item in already_existed_accounts]
        for follower_info in followers_info:
            if follower_info.id not in already_existed_ids:
                follower_document = {
                    ID_KEY: follower_info.id,
                    NAME_KEY: follower_info.name,
                    SURNAME_KEY: follower_info.surname,
                    SECRET_KEY_KEY: self.vk_worker.generate_follower_secret_key(follower_info)
                }
                self.accounts.insert_one(follower_document)
                Utils.log_info(f"Inserted {follower_info.name} {follower_info.surname} into accounts collection")

    # Returns None if there is no account with such id
    def get_user_secret_key_by_id(self, follower_id: int):
        result = self.accounts.find_one({ID_KEY: follower_id})
        if result is not None:
            return result[SECRET_KEY_KEY]
        return None

    def get_user_id_by_secret_key(self, follower_secret_key: str):
        return self.accounts.find_one({SECRET_KEY_KEY: follower_secret_key})

    def get_public_followers_info(self) -> List[PrivateFollowerInfo]:
        public_accounts = self.accounts.find({IS_PUBLIC_KEY: True})
        return [PrivateFollowerInfo(id=account[ID_KEY], name=account[NAME_KEY], surname=account[SURNAME_KEY]) for account
                in
                public_accounts]

    def get_activity_info_csv(self) -> StringIO:
        activities = self.activity_data.find()
        output = StringIO("")
        header_row = list()
        header_data = [ID_KEY, MINUTES_INTERVAL_NUMBER_KEY, DATETIME_KEY, LAST_SEEN_DATETIME_KEY, ONLINE_KEY,
                       PLATFORM_KEY]
        for header_data_item in header_data:
            header_row.append(header_data_item)
        header_string = ",".join([str(instance) for instance in header_row])
        output.write(f"{header_string}\n")

        for activity in activities:
            activity_row = []
            activity_data = [str(activity[ID_KEY]), activity[MINUTES_INTERVAL_NUMBER_KEY], activity[DATETIME_KEY],
                             activity[LAST_SEEN_DATETIME_KEY], activity[ONLINE_KEY], activity[PLATFORM_KEY]]
            for activity_data_item in activity_data:
                activity_row.append(activity_data_item)
            activity_data_string = ",".join([str(instance) for instance in activity_row])
            output.write(f"{activity_data_string}\n")
        output.seek(0)
        return output

    def is_surname_fits_with_secret_key(self, surname: str, secret_key: str) -> bool:
        fit_accounts = list(self.accounts.find({SECRET_KEY_KEY: secret_key}))
        for account in fit_accounts:
            if surname == account[SURNAME_KEY]:
                return True
        return False

    def is_surname_exists(self, surname: str) -> bool:
        fit_accounts = self.accounts.find({SURNAME_KEY: surname})
        return len(list(fit_accounts)) != 0

    def is_id_exists(self, id: int) -> bool:
        fit_accounts = self.accounts.find({ID_KEY: id})
        return len(list(fit_accounts)) != 0

    def is_account_with_id_is_public(self, id):
        account = self.accounts.find({ID_KEY: id})
        return account[IS_PUBLIC_KEY] is True
