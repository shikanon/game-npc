from sqlalchemy import create_engine, Column, String, Integer, Enum, DateTime, ForeignKey, Text, PrimaryKeyConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import List
from datetime import datetime
from urllib.parse import quote_plus
import json
import uuid
import os

# 创建对象的基类
Base = declarative_base()
db_user = os.environ['MYSQL_DB_USER']
db_password = os.environ['MYSQL_DB_PASSWORD']
db_host = os.environ['MYSQL_DB_HOST']
db_database = "game"
db_uri = f'mysql+pymysql://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}/'
print(db_uri)

# 初始化数据库连接:
engine = create_engine(db_uri+db_database)

# 创建DBSession类型:
DBSession = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

class MySQLBaseModel(Base):
    __abstract__ = True  # 声明这是个抽象类

    # 增
    def add(self):
        session = DBSession()
        session.add(self)
        session.commit()
        session.close()

    # 删
    @classmethod
    def delete(cls, id):
        session = DBSession()
        session.query(cls).filter_by(id=id).delete()
        session.commit()
        session.close()

    # 改
    def update(self):
        session = DBSession()
        session.commit()
        session.close()

    # 查
    @classmethod
    def query(cls, id):
        session = DBSession()
        res = session.query(cls).filter_by(id=id).first()
        session.close()
        return res
    
    @classmethod
    def select_records(cls, record_class, order_by=None, filter_dict=None, page=1, limit=10)->List:
        session = DBSession()
        query = session.query(record_class)
        if filter_dict is not None:
            query = query.filter_by(**filter_dict)
        if order_by is not None:
            if isinstance(order_by, str):                      # order_by 默认为升序
                query = query.order_by(text(order_by))
            elif isinstance(order_by, dict):                   # 如果为字典时，key也就是需要排序的字段，value为True则为升序，False则为降序
                for key, value in order_by.items():
                    if value:
                        query = query.order_by(text(key))
                    else:
                        query = query.order_by(text(key + " DESC"))     # 使用sqlalchemy的desc函数进行降序排序
        if page is not None and limit is not None:             # 加入分页功能
            query = query.limit(limit).offset((page-1)*limit)
        results = query.all()
        return results


class NPC(MySQLBaseModel):
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    short_description = Column(String(255))
    trait = Column(Text)
    prompt_description = Column(Text)
    profile = Column(Text)
    chat_background = Column(Text)
    affinity_level_description = Column(Text)
    knowledge_id = Column(String(255))
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = Column(DateTime, default=datetime.now())


class NPCUser(MySQLBaseModel):
        # 表的名字
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    PrimaryKeyConstraint('npc_id', 'user_id'),
    {'extend_existing': True}
    )
    npc_id = Column(String(255), ForeignKey('npc.id'))  # npc配置对象，外键
    # 通过关系关联NPCConfig对象
    npc = relationship('NPC')
    user_id = Column(String(255), ForeignKey('user.id'))  # 用户对象，外键
    # 通过关系关联User对象
    user = relationship('User')
    scene = Column(String(255))  # 场景描述
    score = Column(Integer)  # 好感分数
    affinity_level = Column(Integer)  # 亲密度等级
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

class User(MySQLBaseModel):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    sex = Column(Enum("男", "女", "未知"))
    phone = Column(String(11))
    money = Column(Integer)
    password = Column(String(11))
    created_at = Column(DateTime, default=datetime.now())
    
    def get_npc_user(self, npc_user_id:str, user_id:str, npc_id:str, scene:str)->NPCUser:
        filter_dict = {"id": npc_user_id}
        npc_users = self.npc_manager.get_npc_users(filter_dict=filter_dict)
        if npc_users == None or len(npc_users) == 0:
            npc = self.npc_manager.get_npc(npc_id)
            npc_user = self.npc_manager.create_npc_user(name=npc.name, user_id=user_id, npc_id=npc_id, trait=npc.trait, scene=scene)
        else:
            npc_user = npc_users[0]
        return npc_user

class Scene(MySQLBaseModel):
    __tablename__ = 'scene'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    scene = Column(Text)
    theater = Column(Text)
    theater_event = Column(Text)
    roles = Column(String(255))
    score = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())


class UserOpinion(MySQLBaseModel):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(Text)  # 用户意见
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

    def labels_str_to_list(label_strs:str)->List:
        separator = ','
        labels = label_strs.split(separator)
        return labels
    
    def labels_list_to_str(labels:List)->str:
        labels_str = ",".join(labels)
        return labels_str