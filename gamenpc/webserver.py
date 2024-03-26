# coding:utf-8
import asyncio
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, uvicorn, json, uuid

from gamenpc.utils import logger
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.user import UserManager
from gamenpc.store.mysql_client import MySQLDatabase
from gamenpc.store.redis_client import RedisList


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
redis_db = os.environ.get('REDIS_DATABASE')
redis_client = RedisList(host=redis_host, port=redis_port, user=redis_user, password=redis_password, db=int(redis_db))

npc_manager = NPCManager(mysql_client, redis_client)
user_manager = UserManager(mysql_client, npc_manager)

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
    content_type: str

def response(code=0, message="执行成功", data=None)->any:
    return {"code": code, "msg": message, "data": data}

def get_npc_user(req:ChatRequest=Depends) -> NPCUser:
    try:
        filter_dict = {"id": req.user_id}
        user = user_manager.get_user(filter_dict=filter_dict)
        if user == None:
            return None
        user.npc_manager = npc_manager
        npc_user = user.get_npc_user(npc_id=req.npc_id, user_id=req.user_id, scene=req.scene)
        return npc_user
    except KeyError:
        return None

@router.post("/npc/chat")
async def chat(req: ChatRequest, npc_user_instance=Depends(get_npc_user)):
    if npc_user_instance == None:
        return response(code="-1", message="选择NPC异常: 用户不存在/NPC不存在")
    '''NPC聊天对话'''
    message, affinity_score = await asyncio.gather(
        npc_user_instance.chat(client=redis_client, player_id=req.user_id, content=req.question, content_type=req.content_type),
        npc_user_instance.update_affinity(client=mysql_client, player_id=req.user_id, content=req.question),
    )
    # thought = npc_user_instance.get_thought_context()
    data = {
        "message": message,
        "message_type": "text",
        "affinity_score": affinity_score,
    }
    return response(message="返回成功", data=data)

class NpcUserQueryRequest(BaseModel):
    npc_id: Optional[str] = ""
    user_id: Optional[str] = ""
    order_by: Optional[str] = {"id": False}
    page: Optional[int] = 1
    limit: Optional[int] = 10

@router.post("/npc/get_npc_users")
async def get_npc_users(req: NpcUserQueryRequest):
    '''获取NPC信息'''
    filter_dict = {}
    if req.npc_id != "" and req.user_id != "":
        filter_dict['id'] = f'{req.npc_id}_{req.user_id}'
    if req.page <= 0:
        req.page = 1
    if req.limit <= 0:
        req.limit = 10  
    npc_users = npc_manager.get_npc_users(order_by=req.order_by, filter_dict=filter_dict, page=req.page, limit=req.limit)
    if npc_users == None:
        return response(code=-1, message="Invaild value of npc_id, it not Exists")
    npc_instances = []
    for npc_user in npc_users:
        npc_instances.append(npc_user.get_character_info())
    return response(data=npc_instances)

class NpcUserAllInfoRequest(BaseModel):
    npc_id: Optional[str] = ""
    user_id: Optional[str] = ""

@router.post("/npc/get_npc_all_info")
async def get_npc_all_info(req: NpcUserAllInfoRequest):
    '''获取NPC信息''' 
    npc_all_info = npc_manager.get_npc_all_info(npc_id=req.npc_id, user_id=req.user_id)
    if npc_all_info == None:
        return response(code=-1, message="Invaild value of npc_id/user_id, it not Exists")
    return response(data=npc_all_info)

class DefaultRequest(BaseModel):
    '''
    user_id: 用户 ID
    npc_id: NPC ID
    '''
    user_id: str
    npc_id: str

@router.post("/npc/get_history_dialogue")
async def get_history_dialogue(req: DefaultRequest):

    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=req.user_id)
    if npc_instance == None:
        return response(code=400, message="NPC not found")
    return response(data= [dialogue.to_dict() for dialogue in npc_instance.get_dialogue_context()])

@router.post("/npc/clear_history_dialogue")
async def clear_history_dialogue(req: DefaultRequest):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=req.user_id)
    if npc_instance == None:
        return response(code=400, message="NPC not found")
    npc_instance.re_init(client=redis_client, mysql_client=mysql_client)
    return response(message="记忆、好感重置成功!")

class NPCRequest(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    trait: Optional[str] = ""
    sex: Optional[int] = 0
    short_description: Optional[str] = ""
    prompt_description: Optional[str] = ""
    profile: Optional[str] = ""
    status: Optional[int] = -1
    chat_background: Optional[str] = ""
    affinity_level_description: Optional[str] = ""

@router.post("/npc/create")
async def create_npc(req: NPCRequest):
    npc = npc_manager.set_npc(name=req.name, trait=req.trait, sex=req.sex, short_description=req.short_description,
                               prompt_description=req.prompt_description, profile=req.profile, 
                               chat_background=req.chat_background, affinity_level_description=req.affinity_level_description)
    return response(data=npc.to_dict())

class NPCRemoveRequest(BaseModel):
    id: str

@router.post("/npc/remove")
async def remove_npc(req: NPCRemoveRequest):
    npc = npc_manager.get_npc(npc_id=req.id)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    npc_manager.remove_npc(npc.id)
    return response(message=f'删除 npc {req.id} 成功')

@router.post("/npc/update")
async def update_npc(req: NPCRequest):
    npc = npc_manager.get_npc(npc_id=req.id)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    if req.name != '':
        npc.name = req.name
    if req.trait != '':
        npc.trait = req.trait
    if req.sex != 0:
        npc.sex = req.sex
    if req.short_description != '':
        npc.short_description = req.short_description
    if req.prompt_description != '':
        npc.prompt_description = req.prompt_description
    if req.profile != '':
        npc.profile = req.profile
    if req.chat_background != '':
        npc.chat_background = req.chat_background
    if req.affinity_level_description != '':
        npc.affinity_level_description = req.affinity_level_description
    if req.status >= 0:
        npc.status = req.status
    npc = npc_manager.update_npc(npc)
    return response(data=npc.to_dict())

class NPCUpdateStatusRequest(BaseModel):
    id: Optional[str] = ""
    status: Optional[int] = -1

@router.post("/npc/update_status")
async def update_npc_status(req: NPCUpdateStatusRequest):
    npc = npc_manager.get_npc(npc_id=req.id)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    if req.status != -1:
        npc.status = req.status
    npc = npc_manager.update_npc(npc)
    return response(data=npc.to_dict())

class NpcQueryRequest(BaseModel):
    name: Optional[str] = ""
    order_by: Optional[str] = {"name": False}
    page: Optional[int] = 1
    limit: Optional[int] = 10

@router.post("/npc/query")
async def query_npc(req: NpcQueryRequest):
    filter_dict = {}
    if req.name != "":
        filter_dict['name'] = req.name
    if req.page <= 0:
        req.page = 1
    if req.limit <= 0:
        req.limit = 10 
    npcs = npc_manager.get_npcs(filter_dict=filter_dict, order_by=req.order_by, page=req.page, limit=req.limit)
    return response(data={'list': [npc.to_dict() for npc in npcs], 'total': len(npcs)})

class NpcGetRequest(BaseModel):
    id: Optional[str] = ""

@router.post("/npc/get")
async def query_npc(req: NpcGetRequest):
    if req.id == "":
        return 
    npc = npc_manager.get_npc(npc_id=req.id)
    return response(data=npc.to_dict())

class ShiftSceneRequest(BaseModel):
    npc_id: str
    user_id: str
    scene: Optional[str] = "窝在家里"

@router.post("/npc/shift_scenes")
async def shift_scenes(req: ShiftSceneRequest):
    '''切换场景'''
    npc_user = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=req.user_id)
    if npc_user is None:
        return response(code=400, message="Invaild value of npc_name, it not Exists")
    npc_user.set_scene(client=mysql_client, scene=req.scene)
    return response(message="场景转移成功")

class UserCreateRequest(BaseModel):
    name: str
    sex: Optional[int] = 0
    phone: Optional[str] = ""
    password: str

@router.post("/user/register")
async def user_register(req: UserCreateRequest):
    if req.sex == "" or req.sex is None:
        req.sex = "未知"
    filter_dict = {}
    if req.name is not None:
        filter_dict['name'] = req.name
    user = user_manager.get_user(filter_dict=filter_dict)
    if user != None:
        return response(message='该用户名已注册')
    user = user_manager.set_user(name=req.name, sex=req.sex, phone=req.phone, money=0, password=req.password)
    if user == None:
        return response(message=f'user {req.name} 注册失败')
    else:
        return response(data=user.to_dict())
    
@router.post("/user/login")
async def user_login(req: UserCreateRequest):
    if req.name is None or req.password is None:
        return response(code=400, message=f'user name or password 不能为空')
    filter_dict = {}
    filter_dict['name'] = req.name
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f'user {req.name} 不存在, 请先注册')
    
    if user.password != req.password:
        return response(code=400, message=f'user {req.name} 密码输入错误')
    
    return response(data=user.to_dict())
    
class UserRemoveRequest(BaseModel):
    id: str

@router.post("/user/remove")
async def remove_user(req: UserRemoveRequest):
    user = user_manager.get_user(user_id=req.id)
    if user == None:
        return response(code=400, message=f"user for {req.id} 不存在")
    user_manager.remove_user(user_id=req.id)
    return response(message=f'删除 user {req.id} 成功')

class UserQueryRequest(BaseModel):
    id: Optional[str] = None

@router.post("/user/query")
async def query_user(req: UserQueryRequest):
    filter_dict = {}
    if req.id is None:
        return response(code=400, message=f'id 不能为空')
    filter_dict['id'] = req.id
    user = user_manager.get_user(filter_dict=filter_dict)
    return response(data=user.to_dict())

class UserCreateRequest(BaseModel):
    id: str
    name: Optional[str] = ""
    sex: Optional[int] = -1
    phone: Optional[str] = ""
    password: Optional[str] = ""

@router.post("/user/update")
async def update_user(req: UserCreateRequest):  
    if req.sex == -1:
        req.sex = 0  
    user = user_manager.update_user(id=req.id, name=req.name, sex=req.sex, phone=req.phone, password=req.password)
    if user == None:
        return response(code=400, message=f'user {req.name} 不存在, 请先注册')
    return response(data=user.to_dict())


# file: UploadFile = File(...)
# image_type: int # Unknown = 0, // 未知 Avatar = 1, // 头像 ChatBackground = 2, // 聊天背景

@router.post("/npc/file_upload")
# 使用UploadFile类可以让FastAPI检查文件类型并提供和文件相关的操作和信息
async def upload_file(image_type: int = Form(...), file: UploadFile = File(...)):
    filename = uuid.uuid4()
    file_location = f"{file_path}/{filename}"  
    # 使用 'wb' 模式以二进制写入文件
    with open(file_location, "wb") as f:
        # 读取上传的文件数据
        content = await file.read()
        f.write(content)
    print('image_type: ', image_type)
    message = f"文件 {file.filename} 已经被保存到 {file_location}"
    url = f'http://game-npc.clarkchu.com/images/{filename}'
    return response(message=message, data=url)

if __name__ == "__main__":
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)