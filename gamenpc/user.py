from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from gamenpc.npc import NPC, NPCManager
from gamenpc.store import MySQLDatabase, Base
from typing import List

class User(Base):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))
    sex = Column(Enum("男", "女", "未知"))
    phone = Column(String(11))
    money = Column(Integer)
    created_at = Column(DateTime)

    def __init__(self, id: str, name:str, sex:str, phone:str, money:int, npc_manager: NPCManager):
        self.id = id
        self.name = name
        self.sex = sex
        self.phone = phone
        self.money = money
        self.npc_manager = npc_manager
        self._npc = {}
    
    def get_npc(self, user_name:str, npc_name:str, scene:str)->NPC:
        npc = self.npc_manager.get_npc(user_name=user_name, npc_name=npc_name)
        if npc == None:
            npc_config = self.npc_manager.get_npc_config(npc_name)
            npc = self.npc_manager.create_npc(user_name=user_name, npc_name=npc_name, npc_traits=npc_config.trait, scene=scene)
        return npc
    
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 用户意见ID
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(String(255))  # 用户意见
    created_at = Column(DateTime)  # 创建时间

    def __init__(self, labels, name, content, created_at):
        self.labels = labels
        self.name = name
        self.content = content

    def labels_str_to_list(label_strs:str)->List:
        separator = ','
        labels = label_strs.split(separator)
        return labels
    
    def labels_list_to_str(labels:List)->str:
        labels_str = ",".join(labels)
        return labels_str

class UserManager:
    def __init__(self, client: MySQLDatabase, npc_manager: NPCManager):
        self.client = client
        self.npc_manager = npc_manager
        self._instances = {}
        records = self.client.select_records(User)
        for record in records:
            name = record[1]
            money = record[2]
            self._instances[name] = User(name, money, self.npc_manager)

    def get_user(self, user_name: str) -> User:
        if user_name not in self._instances:
            self._instances[user_name] = User(user_name, 100, self.npc_manager)

        return self._instances.get(user_name)
    
    def set_user(self, user_name: str):
        money = 100
        self._instances[user_name] = User(user_name, money, self.npc_manager)
        user = User(name=user_name, money=money)
        self.client.insert_record(user)