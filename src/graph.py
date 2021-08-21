import random

from src.online_statusplatform import OnlineStatusPlatform

if __name__ == "__main__":
    # One date = 100 intervals

    for i in range(10):
        print(random.randint(1, 27))

    first_person_dates_info = [[True, False, False], [False, False, True], [False, True, True]]
    sedond_person_dates_info = [[False, False, False], [False, False, True], [False, True, True]]