import uuid
import os

from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, text
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from datetime import datetime
from dataclasses import dataclass
from itsdangerous import TimedSerializer, BadData

from gamenpc.npc import NPCUser, NPCManager
from gamenpc.store.mysql_client import MySQLDatabase, Base

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
    is_super = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, name=None, sex=None, phone=None, money=None, password=None):
        self.id = id
        self.name = name
        self.sex = sex
        self.phone = phone
        self.money = money
        self.password = password
        self._npc = {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sex': self.sex,
            'phone': self.phone,
            'money': self.money,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
    
@dataclass
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(Text)  # 用户意见
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), server_onupdate=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
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
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }

    def labels_str_to_list(label_strs:str)->List:
        separator = ','
        labels = label_strs.split(separator)
        return labels
    
    def labels_list_to_str(labels:List)->str:
        labels_str = ",".join(labels)
        return labels_str

class UserManager:
    def __init__(self, mysql_client: MySQLDatabase):
        self.mysql_client = mysql_client
        self.expire_time = 60 * 60 * 24 * 30 # 过期时间为30天
        self.secret_key = os.environ.get('SECRET_KEY')
        if self.secret_key is None:
            self.secret_key = "this-your-default-secret-key"

    def get_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[User]:
        users = self.mysql_client.select_records(record_class=User, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return users
    
    def get_user(self, filter_dict) -> User:
        user = self.mysql_client.select_record(record_class=User, filter_dict=filter_dict)
        if user == None:
            return None
        return user
    
    def set_user(self, name, sex, phone, money, password) -> User:
        # 创建新用户
        user = User(name=name, sex=sex, phone=phone, money=money, password=password)
        user = self.mysql_client.insert_record(user)
        return user
    
    def update_user(self, id, name, sex, phone, password) -> User:
        filter_dict = {'id': id}
        user = self.mysql_client.select_record(record_class=User, filter_dict=filter_dict)
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
        user.updated_at = datetime.now()
        user = self.mysql_client.update_record(user)
        return user
    
    def remove_user(self, user_id: str):
        self.mysql_client.delete_record_by_id(record_class=User, id=user_id)

    # 生成token
    def generate_token(self, username: str, password: str) -> str:
        s = TimedSerializer(self.secret_key, expires_in=self.expire_time)
        token = s.dumps({"username": username, "password": password}).decode()
        self.mysql_client.set_key_expire(token, self.expire_time)
        return token
    
    # 解析token
    def decode_token(self, token:str) -> str:
        s = TimedSerializer(self.secret_key)
        try:
            data = s.loads(token)
            username = data['username']
            return username
        except BadData:
            return ""

    # 验证token
    def verify_token(self, token: str)-> bool:
        username = self.decode_token(token)
        if username == "":
            return False
        if not self.mysql_client.get(token):
            return False
        return True