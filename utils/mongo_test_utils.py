import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class HistoryMongoTool:
    # 初始化方法
    def __init__(self):
        # 获得url,db_name
        self._mongo_url = os.getenv("MONGO_URL")
        self._db_name = os.getenv("MONGO_USERNAME")
        # 链接
        self._client = MongoClient(self._mongo_url)
        # 索引
        self.db = self._client[self._db_name]
        # 集合(表)
        self.chat_message = self.db["chat_message"]
        self.chat_message.create_index([("session_id", 1), ("ts", -1)])
# 实例化
_history_mongo_tool = HistoryMongoTool()

def get_history_mongo_tool():
    global  _history_mongo_tool
    if _history_mongo_tool is None:
        _history_mongo_tool = HistoryMongoTool()
    return _history_mongo_tool
