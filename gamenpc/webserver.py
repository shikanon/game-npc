# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, uvicorn

from gamenpc.utils import logger
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.user import UserManager
from gamenpc.store.mysql import MySQLDatabase
from gamenpc.store.redis import RedisList


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

file_path = os.environ.get('FILE_PATH')

# 加载环境变量并获取 MySQL 相关配置
mysql_host = os.environ.get('MYSQL_HOST')
mysql_port = os.environ.get('MYSQL_PORT')
mysql_user = os.environ.get('MYSQL_USER')
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_database = os.environ.get('MYSQL_DATABASE')
mysql_client = MySQLDatabase(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password, database=mysql_database)

redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT')
redis_user = os.environ.get('REDIS_USER')
redis_password = os.environ.get('REDIS_PASSWORD')
redis_db = os.environ.get('MYSQL_DATABASE')
redis_client = RedisList(host=redis_host, port=redis_port, user=redis_user, password=redis_password, db=redis_db)

npc_manager = NPCManager(mysql_client, redis_client)
user_manager = UserManager(mysql_client, npc_manager)

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
    id: str
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

def get_npc_user(req:ChatRequest=Depends) -> NPCUser:
    try:
        filter_dict = {"id": req.user_id}
        user = user_manager.get_user(filter_dict=filter_dict)
        if user == None:
            return None
        npc_user = user.get_npc_user(npc_user_id=req.id, user_id=req.user_id, npc_id=req.npc_id, scene=req.scene)
        return npc_user
    except KeyError:
        return None

@router.post("/npc/chat")
async def chat(req: ChatRequest, npc_user_instance=Depends(get_npc_user)):
    if npc_user_instance == None:
        return response(code="-1", message="选择NPC异常: 用户不存在/NPC不存在")
    '''NPC聊天对话'''
    answer, affinity_score = await asyncio.gather(
        npc_user_instance.chat(mysql_client, req.user_id, req.question, req.contentType),
        npc_user_instance.update_affinity(mysql_client, req.user_id, req.question),
    )
    thought = npc_user_instance.get_thought_context()
    data = {
        "answer": answer,
        "affinity_score": affinity_score,
        "thought": thought,
    }
    return response(message="返回成功", data=data)

@router.get("/npc/get_npc_user")
async def get_npc_user(npc_user_id: str):
    '''获取NPC信息'''
    filter_dict = {"id": npc_user_id}
    npc_instance = npc_manager.get_npc_users(filter_dict=filter_dict)
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
        npc_instance.re_init(mysql_client)
        return response(message="记忆、好感重置成功!")
    except KeyError:
        return response(code=400, message="NPC not found")

class NpcQueryRequest(BaseModel):
    id: str
    name: str
    order_by: str
    page: int
    per_page: int

@router.get("/npc/query")
async def query_npc(req: NpcQueryRequest):
    filter_dict = {}
    if req.id is not None:
        filter_dict['id'] = req.id
    if req.name is not None:
        filter_dict['name'] = req.name
    npcs = npc_manager.get_npcs(order_by=req.order_by, filter_dict=filter_dict, page=req.page, per_page=req.per_page)
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
    npc_instance.set_scene(client=mysql_client, scene=scene)
    return response(message="场景转移成功")

class UserRequest(BaseModel):
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

class UserQueryRequest(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    sex: Optional[str] = ""
    phone: Optional[str] = ""
    money: Optional[str] = ""
    order_by: Optional[str] = "desc"
    page: Optional[int] = 0
    per_page: Optional[int] = 1

@router.get("/user/query")
async def query_user(req: UserQueryRequest):
    filter_dict = {}
    if req.id is not None:
        filter_dict['id'] = req.id
    if req.name is not None:
        filter_dict['name'] = req.name
    if req.sex is not None:
        filter_dict['sex'] = req.sex
    if req.phone is not None:
        filter_dict['phone'] = req.phone
    if req.money is not None:
        filter_dict['money'] = req.money
    users = user_manager.get_users(order_by=req.order_by, filter_dict=filter_dict, page=req.page, per_page=req.per_page)
    return response(data=users)

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
    # # 上传文件到OBS
    # obs_response = obs_client.putFile(bucket_name, file.filename, file_location)
    # if obs_response.status < 300:
    #     message = f"文件 '{file.filename}' 已经被保存到 '{file_location}' 和 ObjectTypeStorage(OBS)."
    # else:
    #     message = f"文件 '{file.filename}' 已经被保存到'{file_location}'，但没有上传到ObjectTypeStorage(OBS)。"
    message = f"文件 '{file.filename}' 已经被保存到 '{file_location}'"
    return response(message=message)

if __name__ == "__main__":
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)