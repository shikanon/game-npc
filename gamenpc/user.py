from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from gamenpc.npc import NPC, NPCManager
from gamenpc.store import MySQLDatabase, Base
from typing import List
import uuid
from datetime import datetime

class User(Base):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    sex = Column(Enum("男", "女", "未知"))
    phone = Column(String(11))
    money = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, name=None, sex=None, phone=None, money=None, npc_manager=NPCManager):
        self.id = id
        self.name = name
        self.sex = sex
        self.phone = phone
        self.money = money
        self.npc_manager = npc_manager
        self._npc = {}
    
    def get_npc(self, user_id:str, npc_id:str, scene:str)->NPC:
        npc = self.npc_manager.get_npc(user_id=user_id, npc_id=npc_id)
        if npc == None:
            npc_config = self.npc_manager.get_npc_config(npc_id)
            npc = self.npc_manager.create_npc(user_id=user_id, npc_id=npc_id, npc_traits=npc_config.trait, scene=scene)
        return npc
    
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(String(255))  # 用户意见
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

    def __init__(self, labels=None, name=None, content=None):
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
        users = self.client.select_records(record_class=User)
        for user in users:
            self._instances[user.id] = user

    def get_user(self, user_id: str) -> User:
        if user_id not in self._instances:
            return None
        return self._instances.get(user_id)
    
    def set_user(self, user: User) -> User:
        user = self.client.insert_record(user)
        self._instances[user.id] = user
        return user
        