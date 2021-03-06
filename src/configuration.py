import os

from src.configuration_keys import GROUP_ACCESS_TOKEN_KEY

GROUP_ACCESS_TOKEN = os.environ.get(GROUP_ACCESS_TOKEN_KEY, None)
if GROUP_ACCESS_TOKEN is None:
    raise RuntimeError(f"Can't read environment GROUP_ACCESS_TOKEN_KEY variable")

MY_GROUP_ID = 162927036
VK_API_VERSION = "5.131"

DATETIME_ONLY_DATE_FORMAT = '%d.%m.%Y'
DATETIME_TIME_INTERVAL_NAME_FORMAT = '%H:%M'
DATETIME_WRITE_FORMAT = '%Y-%m-%d %H:%M:%S'

MINUTES_INTERVAL = 2
MINUTES_INTERVALS_NUMBER = 24 * 60 // MINUTES_INTERVAL
