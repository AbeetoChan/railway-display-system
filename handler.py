from uuid import uuid4
from redis import Redis
from enum import Enum
from datetime import datetime


class TrainExpectedStatus(Enum):
    ON_TIME = 0
    LATE = 1

    def __int__(self):
        return self.value


class TrainInfoHandler:
    def __init__(self):
        self.db = Redis(port=6379, db=0)

    @staticmethod
    def _generate_uuid():
        return uuid4().hex

    def new_train_data(self, time: datetime, destination: str, platform: int, expected: TrainExpectedStatus):
        uuid_gen = self._generate_uuid()

        with self.db.pipeline() as pipe:
            pipe.hmset(uuid_gen, {
                "time": str(time),
                "destination": destination,
                "platform": platform,
                "expected": int(expected)
            })
            pipe.execute()

        self.db.expireat(uuid_gen, time)

        return uuid_gen

    def get_train_data(self, uuid_gen: str):
        if not self.db.exists(uuid_gen):
            return None

        return {
            "time": self.db.hget(uuid_gen, "time").decode("utf-8"),
            "destination": self.db.hget(uuid_gen, "destination").decode("utf-8"),
            "platform": int(self.db.hget(uuid_gen, "platform")),
            "expected": int(self.db.hget(uuid_gen, "expected"))
        }

    def get_all_train_uuids(self):
        keys = [key.decode("utf-8") for key in self.db.keys("*")]
        return keys

    # Assume train has came late
    def change_train_time(self, uuid_gen: str, new_time: datetime):
        self.db.hset(uuid_gen, "expected", int(TrainExpectedStatus.LATE))
        self.db.expireat(uuid_gen, new_time)
        self.db.hset(uuid_gen, "time", str(new_time))
