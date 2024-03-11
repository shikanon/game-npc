# 接口文档

## 查询角色列表

- 请求方式：GET
- url接口：/api/get_npcs
- 接口请求参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| page_num   | int    | 分页参数，表示当前第几页 |
| limit   | int    | 当前页的查询item的上限 |
| label   | string    | 标签 |


- 返回参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| code   | int    | 错误状态码，0表示一切正常，其他数字表示错误 |
| data   | []npc_object    | 返回npc_object的数据结构 |

- npc_object 数据结构

| 字段名称 | 类型 | 说明 |
|:-----|:-------|:-------|
| npc_name   | string    | npc名称 |
| npc_profile   | string    | npc头像地址 |
| npc_short_description   | string    | npc简介 |


示例代码
```python
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
```

## 创建NPC

- 请求方式：POST
- url接口：/api/npc/create
- 接口请求参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| name   | string    | NPC名称 |
| short_description   | string    | 短描述，主要用于前端展示 |
| trait   | string    | NPC特征，提示词内容（可选） |
| prompt_description   | string    | 提示词描述，存储完整提示词模板(可选) |
| profile   | string    | 头像图片url路径 |
| chat_background   | string    | 聊天背景图片url路径 |
| affinity_level_description   | string    | 亲密度等级行为倾向描述，格式json{"初识": "好奇、谨慎、试探性","熟人": "积极、主动、真诚、调侃","亲密朋友": "关爱、感激、深情、溺爱","心灵伴侣": "互信互依、灵魂融合","敌对": "恐惧、害怕、不甘心",} |

- 返回参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| code   | int    | 错误状态码，0表示一切正常，其他数字表示错误 |
| msg   | string    | 返回消息，创建成功返回“xx 创建成功”的字段 |


```python
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
        new_npc = NPCConfig(
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
```


## 上传图片

- 请求方式：POST
- url接口：/api/uploadfile
- 接口请求参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| file   | 文件    | 上传的文件对象 |

- 返回参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| code   | int    | 错误状态码，0表示一切正常，其他数字表示错误 |
| msg   | string    | 返回消息  |
| url   | string    | 图片地址  |


```python

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

class Result(BaseModel):
    code: int
    msg: str
    url: str = None

def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/api/uploadfile", response_model=Result)
async def create_upload_file(file: UploadFile):
    result = Result(code=0, msg="Upload successful")
    if allowed_file(file.filename):
        try:
            file_location = f"your_path/{file.filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
            result.url = f"http://localhost:8000/img/{file.filename}"
        except Exception as e:
            result.code = 1
            result.msg = str(e)
    else:
        result.code = 1
        result.msg = "Invalid file type"
    return result
```

## NPC聊天

- 请求方式：POST
- url接口：/api/npc/chat
- 接口请求参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| user_id   | string    | 用户 ID |
| npc_id   | string    | NPC ID |
| question   | string    | 问题 |

- 返回参数：

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| code   | int    | 错误状态码，0表示一切正常，其他数字表示错误 |
| msg   | string    | 返回消息 |
| data   |  []answer    |  返回answer数据结构 |

answer对象数据结构：
| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| message   | string    | 错误状态码，0表示一切正常，其他数字表示错误 |
| message_type   | string    | 返回消息 |
| affinity_score   |  string    |  亲密度  |

```python
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
```


# 数据库表结构设计

## 关系数据库

### npc_config表


| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| id   | int    | NPC ID，自增id |
| name | string | NPC名称    |
| short_description | string | 短描述，主要用于前端展示    |
| trait | string | NPC特征，提示词内容    |
| prompt_description | string | 提示词描述，存储完整提示词模板    |
| created_at | datetime | 创建时间    |
| updated_at | datetime | 更新时间    |
| profile | string | 头像图片路径    |
| chat_background | string | 聊天背景图片路径    |
| affinity_level_description | string | 亲密度等级行为倾向描述    |
| knowledge_id | string | 知识库的 index id    |

ORM设计：
```python
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
```

### user表

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| id   | int    | 用户ID，自增id |
| name | string | 用户名称    |
| sex | 枚举 | 性别：男、女、未知    |
| phone | string | 手机号   |
| money | int | 用户虚拟积分    |
| created_at | datetime | 创建时间    |

ORM设计：
```python
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
```

### scene表

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| id   | int    | 场景ID，自增id |
| scene | string | 场景描述    |
| theater | string | 剧情章节   |
| theater_event | string | 剧情的事件（json）   |
| roles | string | 角色描述，角色的背景描述,json格式   |
| score | string | 特定剧场的任务目标，可以是好感也可以是其他值   |

ORM：
```python
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
```


### NPC用户管理表

| 参数字段 | 类型 | 说明 |
|:-----|:-------|:-------|
| id   | int    | 用户ID，自增id |
| npc | 外键 | npc配置对象，外键    |
| user | 外键 | 用户对象，外键    |
| scene | string | 场景    |
| score | int | 好感分数    |
| phone | string | 手机号   |
| money | int | 用户虚拟积分    |
| created_at | datetime | 创建时间    |

ORM:
```python
from sqlalchemy.orm import relationship
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
```



## 缓存数据库redis


