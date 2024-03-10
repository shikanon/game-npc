# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, uvicorn

from gamenpc.utils import logger
from gamenpc.npc import NPC, NPCManager
from gamenpc.user import UserManager
from gamenpc.store import MySQLDatabase


app = FastAPI()
router = APIRouter(prefix="/api")

debuglog = logger.DebugLogger("chat bot web")

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

# 加载环境变量并获取 MySQL 相关配置
host = os.environ.get('MYSQL_HOST')
port = os.environ.get('MYSQL_PORT')
user = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
database = os.environ.get('MYSQL_DATABASE')
db = MySQLDatabase(host=host, port=port, user=user, password=password, database=database)
npc_manager = NPCManager(db)
user_manager = UserManager(db, npc_manager)

class ChatRequest(BaseModel):
    '''
    user_name: 用户名称
    npc_name: NPC的名称
    question: 问题，文本格式
    '''
    user_id: str
    npc_id: str
    scene: str
    question: str
    contentType: str

class NPCRequest(BaseModel):
    user_id: Optional[str] = ""
    npc_id: str
    trait: str
    profile_url: Optional[str] = ""

def get_npc(req:ChatRequest=Depends) -> NPC:
    try:
        user = user_manager.get_user(user_name=req.user_name)
        print(user)
        if req.scene == '':
            req.scene = '宅在家里'
        return user.get_npc_user(req.user_id, req.npc_id, req.scene)
    except KeyError:
        raise HTTPException(status_code=404, detail="NPC not found.")

@router.post("/chat")
async def chat(req: ChatRequest, npc_instance=Depends(get_npc)):
    '''NPC聊天对话'''
    answer, affinity_score = await asyncio.gather(
        npc_instance.chat(db, req.user_name, req.question, req.contentType),
        npc_instance.update_affinity(db, req.user_name, req.question),
    )
    thought = npc_instance.get_thought_context()
    response = {
        "answer": answer,
        "affinity_score": affinity_score,
        "thought": thought,
    }
    return response

@router.get("/npc/get_npc_user")
async def get_npc_user(npc_id: str, user_id: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id, user_id)
    if npc_instance == None:
        return HTTPException(status_code=400, detail="Invaild value of npc_name, it not Exists")
    # if npc_instance.scene == "":
    #     npc_instance.scene = "宅在家中"
    return npc_instance.get_character_info()

@router.get("/npc/get_npc_user_memory")
async def get_npc_user_memory(npc_id: str, user_id: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id, user_id)
    try:
        npc_instance.re_init(db)
        return {"status": "success", "message": "记忆、好感重置成功!"}
    except KeyError:
        return HTTPException(status_code=404, detail="NPC not found.")

@router.get("/npc/clear_npc_user_memory")
async def clear_npc_user_memory(npc_id: str, user_id: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id, user_id)
    try:
        npc_instance.re_init(db)
        return {"status": "success", "message": "记忆、好感重置成功!"}
    except KeyError:
        return HTTPException(status_code=404, detail="NPC not found.")

@router.get("/npc/query")
async def query_npc(npc_id: str):
    '''获取单个NPC配置信息'''
    print('npc_id: ', npc_id)
    if npc_id == "":
        '''获取所有NPC配置信息'''
        return npc_manager.get_all_npc()
    npc_configs = []
    npc_config = npc_manager.get_npc(npc_id)
    npc_configs.append(npc_config)
    return npc_configs

@router.post("/npc/create")
async def create_npc(req: NPCRequest):
    '''设置NPC性格'''
    npc_instance = npc_manager.get_npc(req.npc_id)
    if npc_instance is None:
        npc_instance = npc_manager.set_npc(npc_name=req.npc_id, npc_traits=req.trait)
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
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)