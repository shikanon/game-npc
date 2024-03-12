# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile
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
file_path = os.environ.get('FILE_PATH')
db = MySQLDatabase(host=host, port=port, user=user, password=password, database=database)
npc_manager = NPCManager(db)
user_manager = UserManager(db, npc_manager)

# # 新增记录
# npc = NPC(name="测试", short_description="测试", trait="测试", prompt_description="测试", profile="测试", chat_background="测试", 
#                  affinity_level_description="测试", knowledge_id="测试", updated_at=datetime.datetime.now())
# new_npc = db.insert_record(npc)

# # 修改记录
# new_npc.name = "hahaha"
# new_npc = db.update_record(new_npc)

# # 查询记录
# npcs = db.select_records(NPC)
# print('npc: ', npcs)

# # 新增记录
# db.delete_record_by_id(NPC, new_npc.id)

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

def response(code=0, message="执行成功", data=None)->any:
    return {"code": code, "message": message, "data": data}

def get_npc(req:ChatRequest=Depends) -> NPC:
    try:
        user = user_manager.get_user(user_id=req.user_id)
        print(user)
        if req.scene == '':
            req.scene = '宅在家里'
        return user.get_npc_user(req.user_id, req.npc_id, req.scene)
    except KeyError:
        return None

@router.post("/chat")
async def chat(req: ChatRequest, npc_instance=Depends(get_npc)):
    '''NPC聊天对话'''
    answer, affinity_score = await asyncio.gather(
        npc_instance.chat(db, req.user_name, req.question, req.contentType),
        npc_instance.update_affinity(db, req.user_name, req.question),
    )
    thought = npc_instance.get_thought_context()
    data = {
        "answer": answer,
        "affinity_score": affinity_score,
        "thought": thought,
    }
    return response(message="返回成功", data=data)

@router.get("/npc/get_npc_user")
async def get_npc_user(npc_user_id: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_user_id)
    if npc_instance == None:
        return response(code=400, message="Invaild value of npc_name, it not Exists")
    return response(data=npc_instance.get_character_info())

@router.get("/npc/get_npc_user_memory")
async def get_npc_user_memory(npc_user_id: str):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_user_id)
    try:
        return response(data=npc_instance.get_dialogue_context())
    except KeyError:
        return response(code=400, message="NPC not found")

@router.get("/npc/clear_npc_user_memory")
async def clear_npc_user_memory(npc_user_id):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_user_id)
    try:
        npc_instance.re_init(db)
        return response(message="记忆、好感重置成功!")
    except KeyError:
        return response(code=400, message="NPC not found")

@router.get("/npc/query")
async def query_npc(npc_id: str):
    '''获取单个NPC配置信息'''
    print('npc_id: ', npc_id)
    if npc_id == "":
        '''获取所有NPC配置信息'''
        return npc_manager.get_all_npc()
    npcs = []
    npc = npc_manager.get_npc(npc_id)
    npcs.append(npc)
    return response(data=npcs)

@router.post("/npc/create")
async def create_npc(req: NPCRequest):
    '''设置NPC性格'''
    npc_instance = npc_manager.get_npc(req.npc_id)
    if npc_instance is None:
        npc_instance = npc_manager.set_npc(npc_name=req.npc_id, npc_traits=req.trait)
    else:
        npc_instance.trait = req.trait
    return response(data=npc_instance)

@router.post("/npc/shift_scenes")
async def shift_scenes(user_name:str, npc_name:str, scene:str):
    '''切换场景'''
    npc_instance = npc_manager.get_npc(user_name, npc_name)
    if npc_instance is None:
        return response(code=400, message="Invaild value of npc_name, it not Exists")
    npc_instance.set_scene(client=db, scene=scene)
    return response(message="场景转移成功")

class UserRequest(BaseModel):
    '''
    self.name = name
    self.sex = sex
    self.phone = phone
    self.money = money
    '''
    name: str
    sex: str
    phone: str
    money: str

@router.post("/user/create")
async def create_user(req: UserRequest):
    user = user_manager.set_user(req.name, req.sex, req.phone, req.money)
    return response(data=user)
    
@router.post("/user/remove")
async def remove_user(user_id: str):
    user = user_manager.remove_user(user_id=user_id)
    return response(data=user)

@router.get("/user/query")
async def query_user(user_id: str):
    user = user_manager.get_user(user_id=user_id)
    return response(data=user)

@router.get("/user/update")
async def update_user(req: UserRequest):
    user = user_manager.update_user(req.name, req.sex, req.phone, req.money)
    return response(data=user)

@router.post("/file/upload")
# 使用UploadFile类可以让FastAPI检查文件类型并提供和文件相关的操作和信息
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{file_path}/{file.filename}"  
    # 使用 'wb' 模式以二进制写入文件
    with open(file_location, "wb") as f:
        # 读取上传的文件数据
        content = await file.read()
        f.write(content)
    return response(message=f"文件 '{file.filename}' 已经被保存到 '{file_location}'.")

if __name__ == "__main__":
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)