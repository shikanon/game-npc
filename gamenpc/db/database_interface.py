from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import datetime
import os

from gamenpc.db import database

# 建立和数据库的连接
# 环境变量 MYSQL_DB_CONFIG 数据结构为 “{user}:{password}@{host}”
db_config = os.environ['MYSQL_DB_CONFIG']
db_database = "game"
db_uri = f'mysql+mysqldb://{db_config}/'
engine = create_engine(db_uri+db_database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建FastAPI实例
app = FastAPI()

class NPCObject(BaseModel):
    npc_name: str
    npc_profile: Optional[str] = None
    npc_short_description: Optional[str] = None

class ResponseModel(BaseModel):
    code: int
    data: List[NPCObject]

@app.get("/api/get_npcs", response_model=ResponseModel)
def get_npcs(page_num: int, limit: int, label: str):
    offset_num = (page_num - 1) * limit
    db = SessionLocal()
    
    try:
        npcs_query = db.query(database.NPCConfig).filter(database.NPCConfig.name == label).order_by(database.NPCConfig.id).offset(offset_num).limit(limit).all()
        npcs = []
        for npc in npcs_query:
            npc_object = NPCObject(
                npc_name=npc.name,
                npc_profile=npc.profile,
                npc_short_description=npc.short_description
            )
            npcs.append(npc_object)

        return {"code": 0, "data": npcs}

    except Exception as e:
        return {"code": 1}

    finally:
        db.close()


class NPCRequestModel(BaseModel):
    name: str
    short_description: str
    trait: Optional[str] = None
    prompt_description: Optional[str] = None
    profile: str
    chat_background: str
    affinity_level_description: str

@app.post("/api/npc/create")
def create_npc(npc: NPCRequestModel):
    db = SessionLocal()

    try:
        # 创建新的npc对象
        new_npc = database.NPCConfig(
            name=npc.name,
            short_description=npc.short_description,
            trait=npc.trait,
            prompt_description=npc.prompt_description,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            profile=npc.profile,
            chat_background=npc.chat_background,
            affinity_level_description=npc.affinity_level_description
        )
        # 添加到数据库会话中
        db.add(new_npc)
        # 提交会话
        db.commit()

        # 返回创建成功的信息
        return {"code": 0, "msg": "NPC created successfully"}

    except Exception as e:
        # 发生异常则回滚
        db.rollback()
        # 并返回错误信息
        raise  {"code": 1, "msg": str(e)}

    finally:
        # 关闭数据库会话
        db.close()


class Answer(BaseModel):
    message: str
    message_type: str
    affinity_score: str

class Result(BaseModel):
    code: int
    msg: str
    data: List[Answer] = []

class NPCChat(BaseModel):
    user_id: str
    npc_id: str
    question: str

@app.post("/api/npc/chat", response_model=Result)
async def npc_chat(item: NPCChat):
    ...
    answer = Answer(
        message="This is the message",
        message_type="Text",
        affinity_score="10"
    )
    
    result = Result(code=0, msg="Chat successful", data=[answer])
    return result