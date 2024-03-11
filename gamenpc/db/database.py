from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类
Base = declarative_base()

class NPCConfig(Base):
    # 表的名字
    __tablename__ = 'npc_config'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))
    short_description = Column(String(255))
    trait = Column(String)
    prompt_description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    profile = Column(String(255))
    chat_background = Column(String(255))
    affinity_level_description = Column(String)
    knowledge_id = Column(String(64))


class User(Base):
    # 表的名字
    __tablename__ = 'user'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64))
    sex = Column(Enum("男", "女", "未知"))
    phone = Column(String(11))
    money = Column(Integer)
    created_at = Column(DateTime)


class Scene(Base):
    # 表的名字
    __tablename__ = 'scene'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    scene = Column(String(255))
    theater = Column(String(255))
    theater_event = Column(String(255))
    roles = Column(String)
    score = Column(String(255))


class NPCUser(Base):
    # 表的名字
    __tablename__ = 'npc_user'

    # 表的结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    npc_id = Column(Integer, ForeignKey('npc_config.id'))
    npc = relationship('NPCConfig')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')
    scene = Column(String(255))
    score = Column(Integer)
    phone = Column(String(11))
    money = Column(Integer)
    created_at = Column(DateTime)