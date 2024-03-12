from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.store.mysql import MySQLDatabase, Base
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
    
    def get_npc_users(self, npc_user_id:str, user_id:str, npc_id:str, scene:str)->NPCUser:
        filter_dict = {"id": npc_user_id}
        npc_users = self.npc_manager.get_npcs(filter_dict=filter_dict)
        if npc_users == None or npc_users.__len__ == 0:
            npc_config = self.npc_manager.get_npc_config(npc_id)
            npc_user = self.npc_manager.create_npc(user_id=user_id, npc_id=npc_id, npc_traits=npc_config.trait, scene=scene)
        else:
            npc_user = npc_users[0]
        return npc_user
    
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

    def get_users(self, order_by=None, filter_dict=None, page=1, per_page=10) -> List[User]:
        users = self.client.select_records(User, order_by=order_by, filter_dict=filter_dict, page=page, per_page=per_page)
        return users

    
    def set_user(self, name, sex, phone, money) -> User:
        user = self.client.insert_record(User(name=name, sex=sex, phone=phone, money=money))
        return user
    
    def update_user(self, id, name, sex, phone, money) -> User:
        # self._instances[user.id] = user
        user.name = name
        user.sex = sex
        user.phone = phone
        user.money = money
        user = self.client.update_record(user)
        return user
    
    def remove_user(self, user_id: str):
        self.client.delete_record_by_id(user_id)
        