# coding:utf-8
import time
from fastapi import FastAPI, Depends, HTTPException, APIRouter, File, UploadFile, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, uvicorn, uuid, mimetypes

from gamenpc.utils.logger import debuglog
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.user import UserManager
from gamenpc.utils.config import Config
from gamenpc.tools import generator


app = FastAPI()
router = APIRouter(prefix="/api")

debuglog.info("服务启动....")

origins = [
    "http://management-game-npc.clarkchu.com",
    "http://game-npc.clarkchu.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Access-Control-Allow-Headers", "Authorization",
                   "DNT", "User-Agent", "X-Requested-With", 
                   "If-Modified-Since", "Cache-Control", "Content-Type", "Range"],
)


file_path = os.environ.get('FILE_PATH')
base_file_url = os.environ.get('BASE_FILE_URL')

# 加载环境变量并获取 MySQL 相关配置
config = Config()

npc_manager = NPCManager(mysql_client=config.mysql_client, redis_client=config.redis_client)
user_manager = UserManager(mysql_client=config.mysql_client)

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
        npc_id=req.npc_id
        user_id=req.user_id
        scene=req.scene
        npc_user = npc_manager.get_npc_user(npc_id=npc_id, user_id=user_id)
        if npc_user == None:
            npc = npc_manager.get_npc(npc_id)
            npc_user = npc_manager.create_npc_user(name=npc.name, npc_id=npc_id, user_id=user_id, sex=npc.sex, trait=npc.trait, scene=scene)
        return npc_user
    except KeyError:
        return None

@router.post("/npc/chat")
async def chat(req: ChatRequest, npc_user_instance=Depends(get_npc_user)):
    '''NPC聊天对话'''
    if npc_user_instance == None:
        return response(code="-1", message="选择NPC异常: 用户不存在/NPC不存在")
    message = await npc_user_instance.chat(client=config.redis_client, player_id=req.user_id, content=req.question, content_type=req.content_type),     
    data = {
        "message": message,
        "message_type": "text",
        "affinity_score": 0,
    }
    return response(message="返回成功", data=data)

@router.post("/npc/debug_chat")
async def debug_chat(req: ChatRequest, npc_user_instance=Depends(get_npc_user)):
    '''chat debug 接口,相比chat接口多了dubug相关信息'''
    start_time = time.time()
    #NPC聊天对话接口
    chat_response = await chat(req=req, npc_user_instance=npc_user_instance)
    total_time = time.time() - start_time
    data = chat_response['data']
    data["debug_message"] =  npc_user_instance.debug_info
    data["total_time"] =  total_time
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
        npc_instances.append(npc_user.to_dict())
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
    npc_instance.re_init(client=config.redis_client, mysql_client=config.mysql_client)
    return response(message="记忆、好感重置成功!")

class NPCRequest(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    trait: Optional[str] = ""
    sex: Optional[int] = 0
    short_description: Optional[str] = ""
    profile: Optional[str] = ""
    status: Optional[int] = -1
    chat_background: Optional[str] = ""
    affinity_level_description: Optional[str] = ""

# prompt_description=req.prompt_description
@router.post("/npc/create")
async def create_npc(req: NPCRequest):
    npc = npc_manager.set_npc(name=req.name, trait=req.trait, sex=req.sex, short_description=req.short_description,
                               profile=req.profile, prompt_description="",
                               chat_background=req.chat_background, affinity_level_description=req.affinity_level_description)
    return response(data=npc.id)

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
    if req.profile != '':
        npc.profile = req.profile
    if req.chat_background != '':
        npc.chat_background = req.chat_background
    if req.affinity_level_description != '':
        npc.affinity_level_description = req.affinity_level_description
    if req.status >= 0:
        npc.status = req.status
    npc = npc_manager.update_npc(npc)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
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
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    return response(data=npc.to_dict())

class NpcQueryRequest(BaseModel):
    name: Optional[str] = ""
    order_by: Optional[str] = {"updated_at": False}
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
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
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
    npc_user.set_scene(client=config.mysql_client, scene=req.scene)
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
    filter_dict = {'id': req.id}
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f"user for {req.id} 不存在")
    user_manager.remove_user(user_id=req.id)
    return response(message=f'删除 user {req.id} 成功')

class UserQueryRequest(BaseModel):
    id: Optional[str] = None

@router.post("/user/query")
async def query_user(req: UserQueryRequest):
    if req.id is None:
        return response(code=400, message=f'id 不能为空')
    filter_dict = {'id': req.id}
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f'user记录为空')
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
async def upload_file(image_type: int = Form(...), file: UploadFile = File(...)):
    # 使用UploadFile类可以让FastAPI检查文件类型并提供和文件相关的操作和信息
    if is_image_file(file.filename) == False:
        return response(code=400, message='上传的文件非图片类型')
    if image_type == 0:
        return response(code=400, message='请输入image_type为非0')
    image_type_str = 'unknown'
    if image_type == 1:
        image_type_str = 'avatar'
    elif image_type == 2:
        image_type_str = 'bg'

    full_file_path = f'{file_path}/{image_type_str}'
    if not os.path.exists(full_file_path):
      os.makedirs(full_file_path)

    _, extension = os.path.splitext(file.filename)
    filename = f'{uuid.uuid4()}{extension}'
    file_location = f"{full_file_path}/{filename}"  
    # 使用 'wb' 模式以二进制写入文件
    with open(file_location, "wb") as f:
        # 读取上传的文件数据
        content = await file.read()
        f.write(content)
    message = f"文件 {file.filename} 已经被保存到 {file_location}"
    url = f'{base_file_url}/{image_type_str}/{filename}'
    return response(message=message, data=url)

def is_image_file(filename):
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype and mimetype.startswith('image')

class GenNPCTraitRequest(BaseModel):
    npc_name: str
    npc_sex: Optional[str] = "女"
    npc_short_description: str

@router.post("/tools/generator_npc_trait")
async def generator_npc_trait(req: GenNPCTraitRequest):
    npc_trait = generator.generator_npc_trait(req.npc_name, req.npc_sex, req.npc_short_description)
    return response(code=0, message="执行成功", data=npc_trait)

if __name__ == "__main__":
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)