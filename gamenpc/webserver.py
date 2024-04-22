# coding:utf-8
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Header, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from gamenpc.services.npc import NPCManager, NPCUser, Picture, AffinityRule
from gamenpc.services.user import UserManager
from gamenpc.utils.config import Config
from gamenpc.utils.logger import debuglog
from gamenpc.tools import generator, suggestion
from passlib.context import CryptContext
import time, json
import asyncio
from pydantic import BaseModel
from typing import Optional, List
import os, uuid, mimetypes



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

# 加载环境变量并获取 MySQL 相关配置
config = Config()

npc_manager = NPCManager(mysql_client=config.mysql_client, redis_client=config.redis_client)
user_manager = UserManager(mysql_client=config.mysql_client)

def response(code=0, message="执行成功", data=None)->any:
    return {"code": code, "msg": message, "data": data}

def get_token(authorization: Optional[str] = Header(None)):
    if authorization:
        credentials = authorization.split()
        if credentials[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme.",
            )
        if len(credentials) == 2:
            token = credentials[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header.",
            )
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header not found",
        )

# 这是一个用于解码令牌的依赖项。
def check_user_validate(access_token: str = Depends(get_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = user_manager.verify_token(access_token)
    if user_id == '':
        raise credentials_exception
    return user_id

file_path = os.environ.get('FILE_PATH')
base_file_url = os.environ.get('BASE_FILE_URL')

class ChatRequest(BaseModel):
    user_id: str
    npc_id: str
    scene: str
    question: str
    prologue: Optional[str] = ""
    content_type: str

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
async def chat(req: ChatRequest, npc_user_instance: NPCUser = Depends(get_npc_user), user_id: str= Depends(check_user_validate)):
    '''NPC聊天对话'''
    if npc_user_instance == None:
        return response(code="-1", message="选择NPC异常: 用户不存在/NPC不存在")
    message, affinity_info = await asyncio.gather(
        npc_user_instance.chat(client=config.redis_client, player_id=req.user_id, content=req.question, content_type=req.content_type),     
        npc_user_instance.increase_affinity(config.mysql_client, req.user_id, req.question),
    )
    debuglog.info(f'user_id: {req.user_id}, content: {req.question}, affinity_info: {affinity_info}')
    # affinity_score = affinity_info['score']
    # affinity_level = affinity_info['affinity_level']
    data = {
        "message": message,
        "message_type": "text",
        # "affinity_score": affinity_score,
        # "affinity_level": affinity_level,
    }
    return response(message="返回成功", data=data)

@router.post("/npc/debug_chat")
async def debug_chat(req: ChatRequest, npc_user_instance: NPCUser=Depends(get_npc_user), user_id: str= Depends(check_user_validate)):
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
async def get_npc_users(req: NpcUserQueryRequest, user_id: str= Depends(check_user_validate)):
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
async def get_npc_all_info(req: NpcUserAllInfoRequest, user_id: str= Depends(check_user_validate)):
    '''获取NPC信息''' 
    npc_all_info = npc_manager.get_npc_all_info(npc_id=req.npc_id, user_id=req.user_id)
    if npc_all_info == None:
        return response(code=-1, message="Invaild value of npc_id/user_id, it not Exists")
    return response(data=npc_all_info)


# 定义chat-suggestion请求参数的模型
class ChatSuggestionRequest(BaseModel):
    user_id: str
    npc_id: str

# 定义chat-suggestion返回参数的模型
class SuggestionMessage(BaseModel):
    suggestion_messages: List[str]

class ChatSuggestionResponse(BaseModel):
    code: int
    msg: str
    data: Optional[SuggestionMessage] = None

# chat-suggestion接口实现
@app.post("/api/npc/chat-suggestion", response_model=ChatSuggestionResponse)
async def generate_chat_suggestion(req: ChatSuggestionRequest, user_id: str= Depends(check_user_validate)):
    npc_user = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=user_id)
    dialogues = npc_user.dialogue_manager.get_recent_dialogue(round=1)
    dialogue = "".join(dialogues)
    npc_trait = npc_user.trait
    response = suggestion.generator_dialogue_suggestion(dialogue, npc_trait)
    if response is None:
        return ChatSuggestionResponse(code=1, msg="生成建议回复出错，建议重试", data=suggestions)
    suggestion_messages = [response["1"],response["2"],response["3"]]
    suggestions = SuggestionMessage(suggestion_messages=suggestion_messages)
    return ChatSuggestionResponse(code=0, msg="执行成功", data=suggestions)




class NPCUserRemoveRequest(BaseModel):
    '''
    user_id: 用户 ID
    npc_id: NPC ID
    '''
    user_id: str
    npc_id: str

@router.post("/npc_user/remove")
async def remove_npc_user(req: NPCUserRemoveRequest, user_id: str= Depends(check_user_validate)):
    npc_manager.remove_npc_user(user_id=req.user_id, npc_id=req.npc_id)
    return response(message=f'删除 npc_user {req.user_id} {req.npc_id} 成功')

class DefaultRequest(BaseModel):
    '''
    user_id: 用户 ID
    npc_id: NPC ID
    '''
    user_id: str
    npc_id: str

@router.post("/npc/get_history_dialogue")
async def get_history_dialogue(req: DefaultRequest, user_id: str= Depends(check_user_validate)):
    '''获取NPC信息'''
    npc_instance = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=req.user_id)
    if npc_instance == None:
        return response(code=400, message="NPC not found")
    return response(data= [dialogue.to_dict() for dialogue in npc_instance.get_dialogue_context()])

@router.post("/npc/clear_history_dialogue")
async def clear_history_dialogue(req: DefaultRequest, user_id: str= Depends(check_user_validate)):
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
    affinity_rules: Optional[List[AffinityRule]] = ""
    prologue: Optional[str] = ""
    pictures: Optional[List[Picture]] = None
    affinity_rules: Optional[List[AffinityRule]] = None
    preset_problems: Optional[List[str]] = None

# prompt_description=req.prompt_description
@router.post("/npc/create")
async def create_npc(req: NPCRequest, user_id: str= Depends(check_user_validate)):
    npc = npc_manager.set_npc(id=req.id, name=req.name, trait=req.trait, sex=req.sex, short_description=req.short_description,
                               profile=req.profile, prompt_description="",
                               chat_background=req.chat_background, affinity_rules=req.affinity_rules,
                               prologue=req.prologue, pictures=req.pictures, preset_problems=req.preset_problems)
    return response(data=npc.id)

class NPCRemoveRequest(BaseModel):
    id: str

@router.post("/npc/remove")
async def remove_npc(req: NPCRemoveRequest, user_id: str= Depends(check_user_validate)):
    npc = npc_manager.get_npc(npc_id=req.id)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    npc_manager.remove_npc(npc.id)
    return response(message=f'删除 npc {req.id} 成功')

@router.post("/npc/update")
async def update_npc(req: NPCRequest, user_id: str= Depends(check_user_validate)):
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
    if req.status >= 0:
        npc.status = req.status
    if req.prologue != '':
        npc.prologue = req.prologue
    if req.pictures != None and len(req.pictures) != 0:
        npc.pictures = req.pictures
    if req.affinity_rules != None and len(req.affinity_rules) != 0:
        npc.affinity_rules = req.affinity_rules
    if req.preset_problems != None and len(req.preset_problems) != 0:
        npc.preset_problems = req.preset_problems
    npc = npc_manager.update_npc(npc)
    if npc == None:
        return response(code=400, message=f"npc for {req.id} 不存在")
    return response(data=npc.to_dict())

class NPCUpdateStatusRequest(BaseModel):
    id: Optional[str] = ""
    status: Optional[int] = -1

@router.post("/npc/update_status")
async def update_npc_status(req: NPCUpdateStatusRequest, user_id: str= Depends(check_user_validate)):
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
    npcs, total = npc_manager.get_npcs(filter_dict=filter_dict, order_by=req.order_by, page=req.page, limit=req.limit)
    return response(data={'list': [npc.to_dict() for npc in npcs], 'total': total})

class NpcGetRequest(BaseModel):
    id: str
    lv: Optional[int] = 0

@router.post("/npc/get_picture")
async def npc_get_picture(req: NpcGetRequest, user_id: str= Depends(check_user_validate)):
    npc_id = req.id
    npc = npc_manager.get_npc(npc_id=npc_id)
    pictures = npc.pictures

    index = req.lv - 1
    if req.lv == 0:
        index = 0
    if index > len(pictures) - 1 or index < 0:
        index = 0
    picture = pictures[index]
    debuglog.info(f'npc_get_picture: update picture_index === {index}, picture === {picture}')
    return response(data=picture)

@router.post("/npc/get_prologue")
async def npc_get_prologue(req: NpcGetRequest, user_id: str= Depends(check_user_validate)):
    npc_id = req.id
    npc = npc_manager.get_npc(npc_id=npc_id)
    prologue = npc.prologue

    debuglog.info(f'npc_get_prologue: get prologue for npc {npc_id} === {prologue}')
    return response(data=prologue)

@router.post("/npc/get_preset_problems")
async def npc_preset_problems(req: NpcGetRequest, user_id: str= Depends(check_user_validate)):
    npc_id = req.id
    npc = npc_manager.get_npc(npc_id=npc_id)
    preset_problems = npc.preset_problems

    debuglog.info(f'npc_preset_problems: get preset_problems for npc {npc_id} === {preset_problems}')
    return response(data=preset_problems)

@router.post("/npc/get")
async def get_npc(req: NpcGetRequest, user_id: str= Depends(check_user_validate)):
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
async def shift_scenes(req: ShiftSceneRequest, user_id: str= Depends(check_user_validate)):
    '''切换场景'''
    npc_user = npc_manager.get_npc_user(npc_id=req.npc_id, user_id=req.user_id)
    if npc_user is None:
        return response(code=400, message="Invaild value of npc_name, it not Exists")
    npc_user.set_scene(client=config.mysql_client, scene=req.scene)
    return response(message="场景转移成功")

# file: UploadFile = File(...)
# image_type: int # Unknown = 0, // 未知 Avatar = 1, // 头像 ChatBackground = 2, // 聊天背景

@router.post("/npc/file_upload")
async def upload_file(image_type: int = Form(...), file: UploadFile = File(...), user_id: str= Depends(check_user_validate)):
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
async def generator_npc_trait(req: GenNPCTraitRequest, user_id: str= Depends(check_user_validate)):
    npc_trait = generator.generator_npc_trait(req.npc_name, req.npc_sex, req.npc_short_description)
    return response(code=0, message="执行成功", data=npc_trait)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(stored_password, provided_password):
    """
    验证密码是否有效
    Args:
        stored_password(string): 数据库中的存储的已哈希的密码
        provided_password(string): 用户输入进来的密码
    Returns:
        result: 返回布尔值，即密码是否匹配
    """
    return pwd_context.verify(secret=provided_password, hash=stored_password)

class UserCreateRequest(BaseModel):
    id: Optional[str] = ''
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
    password_hash = get_password_hash(req.password)
    user = user_manager.set_user(id=req.id, name=req.name, sex=req.sex, phone=req.phone, money=0, password=password_hash)
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
    if verify_password(user.password, req.password) == False:
        return response(code=400, message=f'user {req.name} 密码输入错误')
    access_token, expires_in = user_manager.generate_token(id=user.id)
    user_data = user.to_dict()
    user_data['access_token'] = access_token
    # user_data['token_type'] = 'bearer'
    # user_data['expires_in'] = expires_in
    return response(data=user_data)

@router.get("/user/verify")
async def user_get(user_id: str= Depends(check_user_validate)):
    filter_dict = {}
    filter_dict['id'] = user_id
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f'user 不存在, 请先注册')
    return response(data=user.to_dict())
    

@router.post("/user/remove")
async def remove_user(user_id: str= Depends(check_user_validate)):
    filter_dict = {'id': user_id}
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f"user {user_id} 不存在")
    user_manager.remove_user(user_id=user_id)
    return response(message=f'删除 user {user_id} 成功')


@router.post("/user/query")
async def query_user(user_id: str= Depends(check_user_validate)):
    filter_dict = {'id': user_id}
    user = user_manager.get_user(filter_dict=filter_dict)
    if user == None:
        return response(code=400, message=f'user记录为空')
    return response(data=user.to_dict())

class UserUpdateRequest(BaseModel):
    name: Optional[str] = ""
    sex: Optional[int] = -1
    phone: Optional[str] = ""
    password: Optional[str] = ""

@router.post("/user/update")
async def update_user(req: UserUpdateRequest, user_id: str= Depends(check_user_validate)):  
    if req.sex == -1:
        req.sex = 0  
    password_hash = get_password_hash(req.password)
    user = user_manager.update_user(id=user_id, name=req.name, sex=req.sex, phone=req.phone, password=password_hash)
    if user == None:
        return response(code=400, message=f'user {req.name} 不存在, 请先注册')
    return response(data=user.to_dict())

if __name__ == "__main__":
    # 创建一个全局对象
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8888)