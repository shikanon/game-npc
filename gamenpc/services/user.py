import uuid
import os

from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, text
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Tuple
from datetime import datetime
from dataclasses import dataclass

from gamenpc.store.mysql_client import MySQLDatabase, Base
from datetime import datetime
from jwt import JWT, jwk_from_dict
import jwt
from datetime import datetime, timedelta
import base64

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
    password = Column(String(255))
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
        self.jwttoken = JWT()
        self.expire_time = 60 # 过期时间为30天
        secret_key = os.environ.get('SECRET_KEY')
        if secret_key is None:
            secret_key = "this-your-default-secret-key"
        secret_key = base64.urlsafe_b64encode(secret_key.encode()).decode()
        self.secret_key = jwk_from_dict({"kty": "oct", "k": secret_key})

    def get_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> Tuple[List[User], int]:
        users, total = self.mysql_client.select_records(record_class=User, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return users, total
    
    def get_user(self, filter_dict) -> User:
        user = self.mysql_client.select_record(record_class=User, filter_dict=filter_dict)
        if user == None:
            return None
        return user
    
    def set_user(self, id, name, sex, phone, money, password) -> User:
        # 创建新用户
        user = User(name=name, sex=sex, phone=phone, money=money, password=password)
        if id != "":
            user = User(id=id, name=name, sex=sex, phone=phone, money=money, password=password)
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
    def generate_token(self, id: str, expires_delta=None) -> Tuple[str, int]:
        to_encode = {'id': id}
        if expires_delta:
            expire = (datetime.now() + expires_delta).timestamp()
        else:
            expire = (datetime.now() + timedelta(minutes=self.expire_time)).timestamp()
        expire_in = int(expire)
        to_encode.update({"exp": expire_in})
        encoded_jwt = self.jwttoken.encode(payload=to_encode, key=self.secret_key, alg="HS256")
        return encoded_jwt, expire_in
    
    # 解析token
    def decode_token(self, token:str) -> str:
        try:
            payload = self.jwttoken.decode(message=token, key=self.secret_key, algorithms=["HS256"])
            user_id: str = payload.get("id")
            return user_id
        except Exception:
            return ""

    # 验证token
    def verify_token(self, token: str)-> User:
        user_id = self.decode_token(token)
        if user_id == "":
            return None
        filter_dict = {"id": user_id}
        user = self.get_user(filter_dict=filter_dict)
        if not user:
            return None
        return user