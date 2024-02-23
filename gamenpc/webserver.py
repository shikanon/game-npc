# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict

from gamenpc.utils import logger
from gamenpc.npc import NPC, NPCManager

app = FastAPI()
router = APIRouter(prefix="/api")
app.include_router(router)

npc_manager = NPCManager()

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
default_npc = npc_manager.create_npc("西门牛牛", trait)

class UserObject:
    def __init__(self, user_name:str, money:int, npc_manager: NPCManager):
        self.user_name = user_name
        self.money = money
        self.npc_manager = npc_manager
        self._npc = {}
    
    def get_npc(self, npc_name:str)->NPC:
        return self.npc_manager.get_npc(npc_name=npc_name)

class UserManager:
    def __init__(self):
        self._instances = {}

    def get_user(self, user_name: str) -> UserObject:
        if user_name not in self._instances:
            self._instances[user_name] = UserObject(user_name, 100, npc_manager)
        return self._instances[user_name]

# 创建一个全局对象
user_manager = UserManager()

class ChatRequest(BaseModel):
    '''
    user_name: 用户名称
    question: 问题，文本格式
    '''
    user_name: str
    npc_name: str
    question: str


def get_npc(req:ChatRequest=Depends) -> NPC:
    try:
        user = user_manager.get_user(user_name=req.user_name)
        print(user)
        return user.get_npc(req.npc_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="NPC not found.")

@router.post("/chat")
async def chat(req: ChatRequest, npc_instance=Depends(get_npc)):
    '''NPC聊天对话'''
    answer, affinity_score = await asyncio.gather(
        npc_instance.chat(req.user_name, req.question),
        npc_instance.update_affinity(req.user_name, req.question),
    )
    thought = npc_instance.get_thought_context()
    response = {
        "answer": answer,
        "affinity_score": affinity_score,
        "thought": thought,
    }
    return response

@router.get("/npc-info")
async def get_npc_info(npc_name:str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc(npc_name)
    print(npc_instance)
    if npc_instance.scene == "":
        npc_instance.scene = "宅在家中"
    return npc_instance.get_character_info()

@router.get("/npc/clear_memory")
async def clear_memory(npc_name:str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc(npc_name)
    try:
        npc_instance.re_init()
        return {"status": "success", "message": "记忆、好感重置成功!"}
    except KeyError:
        return HTTPException(status_code=404, detail="NPC not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)