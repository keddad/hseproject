from enum import Enum
from typing import List, Dict


class TaskStatus(Enum):
    PENDING = 0,
    DONE = 1,
    ERR = 2


class Task:
    status: TaskStatus
    output: List[List[Dict]]
    err: str

    def __init__(self):
        self.status = TaskStatus.PENDING
        self.err = ""
        self.output = []

    def __str__(self):
        return f"{self.status} {self.err} {self.output}"


class GlobalCache:
    __cache = dict()

    def __contains__(self, item):
        return item in self.__cache

    def __getitem__(self, item):
        return self.__cache[item]

    def __setitem__(self, key, value):
        self.__cache[key] = value
