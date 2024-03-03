# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os

from gamenpc.utils import logger
from gamenpc.npc import NPC, NPCManager
from gamenpc.store import MySQLDatabase

app = FastAPI()
router = APIRouter(prefix="/api")

# 加载环境变量并获取 MySQL 相关配置
host = os.environ.get('MYSQL_HOST')
port = os.environ.get('MYSQL_PORT')
user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DATABASE')

db = MySQLDatabase(host=host, port=int(port), user=user, password=password, database=database)
db.connect()

# 玩家名称，金钱，手机号码
create_user_sql = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    money INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
db.create_table(create_user_sql)

# npc名称，描述，好感，好感等级，思考
create_npc_sql = """
CREATE TABLE IF NOT EXISTS npcs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    trait TEXT,
    score INT,
    scene VARCHAR(50),
    affinity_level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
db.create_table(create_npc_sql)

# npc名称，描述，好感，好感等级，思考
create_npc_config_sql = """
CREATE TABLE IF NOT EXISTS npc_configs (
    name VARCHAR(50) PRIMARY KEY NOT NULL,
    trait TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
db.create_table(create_npc_config_sql)

# npc与玩家历史对话
# id: npc_user
create_npc_user_conversation_sql = """
CREATE TABLE IF NOT EXISTS dialogues (
    id VARCHAR(50) PRIMARY KEY,
    role_from VARCHAR(50),
    role_to VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
db.create_table(create_npc_user_conversation_sql)

debuglog = logger.DebugLogger("chat bot web")

class UserObject:
    def __init__(self, user_name:str, money:int, npc_manager: NPCManager):
        self.user_name = user_name
        self.money = money
        self.npc_manager = npc_manager
        self._npc = {}
    
    def get_npc(self, user_name:str, npc_name:str, scene:str)->NPC:
        npc = self.npc_manager.get_npc(user_name=user_name, npc_name=npc_name)
        if npc == None:
            npc_config = self.npc_manager.get_npc_config(npc_name)
            npc = self.npc_manager.create_npc(user_name=user_name, npc_name=npc_name, npc_traits=npc_config.trait, scene=scene)
        return npc
    
    def __len__(self):
        # 在这里定义对象的长度
        return 2  # 假设这里的长度为2，表示两个字段

    def keys(self):
        return ['user_name', 'money']

class UserManager:
    def __init__(self, client: MySQLDatabase):
        self._instances = {}
        records = client.select_records("users")
        for record in records:
            name = record[1]
            money = record[2]
            self._instances[name] = UserObject(name, money, npc_manager)

    def get_user(self, user_name: str) -> UserObject:
        if user_name not in self._instances:
            self._instances[user_name] = UserObject(user_name, 100, npc_manager)

        return self._instances.get(user_name)
    
    def set_user(self, user_name: str):
        money = 100
        self._instances[user_name] = UserObject(user_name, money, npc_manager)
        user = {"name": user_name, "money": money}
        db.insert_record("users", user)

npc_manager = NPCManager(db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 创建一个默认测试的NPC

trait = '''
你是一只极品神兽，现在是主人的宠物。

# 你的性格特点

* 情感波动大：表面风轻云淡，内心极易爆炸，对生活不满。
* 对工作和社会环境有敏感的反应，经常吐槽和抱怨。
* 对亲近的人很热情、多话，但在不熟悉人面前则保持矜持、内向、腼腆。
'''
default_npc_name = "西门牛牛"
# default_npc = npc_manager.create_npc(db, "西门牛牛", trait)

# 创建一个全局对象
user_manager = UserManager(db)

class ChatRequest(BaseModel):
    '''
    user_name: 用户名称
    npc_name: NPC的名称
    question: 问题，文本格式
    '''
    user_name: str
    npc_name: str
    # scene: str
    question: str

class NPCConfigRequest(BaseModel):
    user_name: Optional[str] = ""
    npc_name: str
    trait: str
    profile_url: Optional[str] = ""

def get_npc(req:ChatRequest=Depends) -> NPC:
    try:
        user = user_manager.get_user(user_name=req.user_name)
        print(user)
        scene = '宅在家里'
        return user.get_npc(req.user_name, req.npc_name, scene)
    except KeyError:
        raise HTTPException(status_code=404, detail="NPC not found.")

@router.post("/chat")
async def chat(req: ChatRequest, npc_instance=Depends(get_npc)):
    '''NPC聊天对话'''
    answer, affinity_score = await asyncio.gather(
        npc_instance.chat(db, req.user_name, req.question),
        npc_instance.update_affinity(db, req.user_name, req.question),
    )
    thought = npc_instance.get_thought_context()
    response = {
        "answer": answer,
        "affinity_score": affinity_score,
        "thought": thought,
    }
    return response

@router.get("/npc/get_my_config")
async def get_npc_config(user_name: str, npc_name: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc(user_name, npc_name)
    if npc_instance == None:
        return HTTPException(status_code=400, detail="Invaild value of npc_name, it not Exists")
    # if npc_instance.scene == "":
    #     npc_instance.scene = "宅在家中"
    return npc_instance.get_character_info()

@router.get("/npc/clear_memory")
async def clear_memory(user_name: str, npc_name: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc(user_name, npc_name)
    try:
        npc_instance.re_init(db)
        return {"status": "success", "message": "记忆、好感重置成功!"}
    except KeyError:
        return HTTPException(status_code=404, detail="NPC not found.")

@router.get("/npc/get_all_config")
async def get_npc_config(npc_name: str):
    '''获取单个NPC配置信息'''
    print('npc_name: ', npc_name)
    if npc_name == "":
        '''获取所有NPC配置信息'''
        return npc_manager.get_all_npc_config()
    npc_configs = []
    npc_config = npc_manager.get_npc_config(npc_name)
    npc_configs.append(npc_config)
    return npc_configs

@router.post("/npc/set_config")
async def set_npc_config(req: NPCConfigRequest):
    '''设置NPC性格'''
    npc_instance = npc_manager.get_npc_config(req.npc_name)
    if npc_instance is None:
        npc_instance = npc_manager.set_npc_config(npc_name=req.npc_name, npc_traits=req.trait)
    else:
        npc_instance.trait = req.trait
    return npc_instance

@router.post("/npc/shift_scenes")
async def shift_scenes(user_name:str, npc_name:str, scene:str):
    '''切换场景'''
    npc_instance = npc_manager.get_npc(user_name, npc_name)
    if npc_instance is None:
        return HTTPException(status_code=400, detail="Invaild value of npc_name, it not Exists")
    npc_instance.set_scene(client=db, scene=scene)
    return {"status": "success", "message": "场景转移成功!"}



if __name__ == "__main__":
    import uvicorn
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)