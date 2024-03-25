from sqlalchemy import Column, String, Integer, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.store.mysql_client import MySQLDatabase, Base
from typing import List
import uuid
from datetime import datetime
from dataclasses import dataclass

@dataclass
class User(Base):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    sex = Column(Integer)
    phone = Column(String(11))
    money = Column(Integer)
    password = Column(String(11))
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, name=None, sex=None, phone=None, money=None, password=None, npc_manager=NPCManager):
        self.id = id
        self.name = name
        self.sex = sex
        self.phone = phone
        self.money = money
        self.password = password
        self.npc_manager = npc_manager
        self._npc = {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sex': self.sex,
            'phone': self.phone,
            'money': self.money,
            'password': self.password,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
    
    def get_npc_user(self, npc_id:str, user_id:str, scene:str)->NPCUser:
        npc_user = self.npc_manager.get_npc_user(npc_id=npc_id, user_id=user_id)
        if npc_user == None:
            npc = self.npc_manager.get_npc(npc_id)
            npc_user = self.npc_manager.create_npc_user(name=npc.name, npc_id=npc_id, user_id=user_id, sex=npc.sex, trait=npc.trait, scene=scene)
        return npc_user
    
@dataclass
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(Text)  # 用户意见
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

    def __init__(self, labels=None, name=None, content=None):
        self.labels = labels
        self.name = name
        self.content = content

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'labels': self.labels,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }

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

    def get_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[User]:
        users = self.client.select_records(User, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return users
    
    def get_user(self, user_id) -> User:
        filter_dict = {'id': user_id}
        user = self.client.select_record(User, filter_dict=filter_dict)
        if user == None:
            return None
        return user
    
    def set_user(self, name, sex, phone, money, password) -> User:
        # 创建新用户
        user = User(name=name, sex=sex, phone=phone, money=money, password=password)
        user = self.client.insert_record(user)
        return user
    
    def update_user(self, id, name, sex, phone, password) -> User:
        filter_dict = {'id': id}
        user = self.client.select_record(User, filter_dict=filter_dict)
        if user == None:
            return None
        if name != "":
            user.name = name
        if sex != "":  
            user.sex = sex
        if phone != "":
            user.phone = phone
        if password != "": 
            user.password = password
        user = self.client.update_record(user)
        return user
    
    def remove_user(self, user_id: str):
        self.client.delete_record_by_id(User, user_id)
        