import datetime
import json
from dataclasses import dataclass
from random import randint
from time import sleep
from typing import List
from urllib.request import urlopen

import vk

from src.configuration import MINUTES_INTERVAL, MY_GROUP_ID, VK_API_VERSION, DATETIME_TIME_INTERVAL_NAME_FORMAT


# TODO: write check for user online between time intervals

@dataclass
class FollowerInfo:
    id: int
    name: str
    surname: str


@dataclass
class FollowerActivityInfo:
    id: int
    minutes_interval_number: int
    datetime: datetime.datetime
    last_seen_datetime: datetime.datetime
    online: bool
    platform: int


class VkWorker:
    def __init__(self, token: str):
        self.session = vk.Session(access_token=token)
        self.vk_api = vk.API(self.session)

    def get_followers_activity_info(self, current_date: datetime.datetime, followers_info: List[FollowerInfo]):
        current_minutes_interval = (current_date.time().hour * 60 + current_date.time().minute) // MINUTES_INTERVAL
        follower_ids = [follower_info.id for follower_info in followers_info]

        followers_activity_info = []
        for follower_id in follower_ids:
            user_info = self.vk_api.users.get(user_id=follower_id, fields="online, last_seen", v=VK_API_VERSION)[0]
            last_seen_info = user_info['last_seen']
            online, last_seen_time, platform = user_info['online'], int(last_seen_info['time']), int(
                last_seen_info['platform'])

            # utcfromtimestamp converts long number into datetime format
            # adding timedelta for what?
            last_seen_time_datetime = (
                    datetime.datetime.utcfromtimestamp(last_seen_time) + datetime.timedelta(hours=5)).strftime(DATETIME_TIME_INTERVAL_NAME_FORMAT)
            followers_activity_info.append(
                FollowerActivityInfo(
                    follower_id,
                    current_minutes_interval,
                    current_date,
                    last_seen_time_datetime,
                    online,
                    platform)
            )

            # Workaround over Vk API in a second requests
            sleep(0.1)
        return followers_activity_info

    def get_followers_info(self) -> List[FollowerInfo]:
        followers_ids = self.vk_api.groups.getMembers(group_id=MY_GROUP_ID, v=VK_API_VERSION)["items"]
        followers_info = []
        for index, user_id in enumerate(followers_ids):
            follower_info = self.get_follower_info_by_id(user_id)
            followers_info.append(follower_info)
        return followers_info

    def get_follower_info_by_id(self, follower_id: int) -> FollowerInfo:
        whole_user_info = self.vk_api.users.get(user_id=follower_id, v=VK_API_VERSION)[0]
        return FollowerInfo(follower_id, whole_user_info["first_name"], whole_user_info["last_name"])

    @staticmethod
    def generate_follower_secret_key(follower_info: FollowerInfo):
        url = "https://dog.ceo/api/breeds/list/all"
        response = urlopen(url)
        data_json = json.loads(response.read())
        dog_names = []
        for item in data_json["message"]:
            if len(data_json["message"][item]) != 0:
                for sub_item in data_json["message"][item]:
                    dog_names.append(f"{item}_{sub_item}")
            else:
                dog_names.append(item)

        return f"{dog_names[follower_info.id % len(dog_names)]}_{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}"

    def get_bot_info(self):
        return self.vk_api.groups.getLongPollServer(group_id=MY_GROUP_ID, v=VK_API_VERSION)

    def get_community_posts_text(self):
        community_posts_info = self.vk_api.wall.get(owner_id=-MY_GROUP_ID, offset=100, count=100, v=VK_API_VERSION)
        # pprint(community_posts_info)
        return [post["text"] for post in community_posts_info["items"]]
