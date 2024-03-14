# 接口文档

接口名称：NPC聊天接口
接口路径(URL)：/npc/chat
请求方式：POST

接口请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|------------------|
| id      | str      | 是 | 无 | ID |
| user_id | str      | 是 | 无 | 用户ID |
| npc_id  | str      | 是 | 无 | NPC的ID |
| scene   | str      | 是 | 无 | 场景 |
| question| str      | 是 | 无 | 用户问题 |
| content_type | str | 是 | 无 | 内容类型 |

接口响应数据：

响应方法 `response(code=0, message="执行成功", data=None)`
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|------------------|
| code    | int  | 是 | 0 | 响应状态码，0表示执行成功 |
| msg     | str  | 是 | "执行成功" | 返回的消息说明 |
| data    | data  | 否 | None | 返回的具体数据内容 |

data的格式
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-----|
| message | str | 是 | 无 | 存储具体的消息内容 |
| message_type | str | 是 | "text" | 消息类型，此处为文本 |
| affinity_score | int/float | 是 | 无 | 亲和力得分 |


接口名称：获取NPC信息
接口路径(URL)：/npc/get_npc_users
请求方式：GET

请求参数 `NpcUserQueryRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| id      | str      | 否 | "" | NPC的ID，不填写或者填写""表示查询所有NPC |
| order_by| str      | 否 | "desc" | 排序方式，desc表示降序，asc表示升序 |
| page    | int      | 否 | 0 | 分页查询的页码，从0开始 |
| limit   | int      | 否 | 1 | 每页的数量 |

接口响应数据：
响应方法 `response(data=npc_instances)`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code    | int  | 是 | 0 | 响应状态码，0表示执行成功，-1表示查询内容不存在 |
| msg     | str  | 是 | "执行成功"或“Invaild value of npc_id, it not Exists” | 返回的消息说明 |
| data    | []user  | 否 | None | 返回的具体数据内容，这里是NPC的详细信息 |

接口名称：获取NPC历史对话
接口路径(URL)：/npc/get_history_dialogue
请求方式：GET

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_user_id | str | 是 | 无 | NPC用户ID |

接口响应数据：
响应方法 `response(data=npc_instance.get_dialogue_context())`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|----------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg | str | 是 | "执行成功"或"NPC not found" | 返回的消息说明 |
| data | []string | 否 | None | 返回的具体数据内容，这里是NPC的历史对话 |


接口名称：重置NPC历史对话
接口路径(URL)：/npc/clear_history_dialogue
请求方式：GET

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_user_id | str | 是 | 无 | NPC用户ID |

接口响应数据：
响应方法 `response(message="记忆、好感重置成功!")`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|--------------------|----------|--------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg  | str | 是 | "记忆、好感重置成功!"或"NPC not found" | 返回的消息说明 |
| data | any | 否 | None | 对于这个请求，一般data项为空 |


接口名称：设置NPC性格
接口路径(URL)：/npc/create
请求方式：POST

请求参数 `NPCRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| name | str | 是 | 无 | NPC的名字 |
| trait | str | 是 | 无 | NPC的性格特点 |
| short_description | str | 否 | "" | NPC的简短描述 |
| prompt_description | str | 是 | 无 | NPC的提示描述 |
| profile | str | 是 | 无 | NPC的个人资料 |
| chat_background | str | 是 | 无 | NPC的聊天背景 |
| affinity_level_description | str | 是 | 无 | NPC的亲和级别描述 |

接口响应数据：
响应方法 `response(data=npc.to_dict())`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | npc | 否 | None | 返回的具体数据内容，是一个包含新创建NPC所有信息的字典 |


接口名称：查询NPC
接口路径(URL)：/npc/query
请求方式：POST

请求参数 `NpcQueryRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| id | str | 否 | 无 | 要查询的NPC的ID |
| name | str | 否 | 无 | 要查询的NPC的名字 |
| order_by | dict | 否 | {"id": False} | 结果排序的字段和顺序 |
| page | int | 否 | 1 | 请求的页数 |
| limit | int | 否 | 10 | 每页返回结果的数量 |

接口响应数据：
响应方法 `response(data=json.dumps([npc.to_dict() for npc in npcs]))`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | []npc | 否 | None | 返回的具体数据内容，这是一个JSON格式的字符串，每一项包含一个查询到的NPC的所有信息 |


接口名称：切换场景
接口路径(URL)：/npc/shift_scenes
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_user_id | str | 是 | 无 | NPC用户ID |
| scene | str | 是 | 无 | 要切换的场景 |

接口响应数据：
响应方法 `response(message="场景转移成功")`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|--------------------|----------|--------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg  | str | 是 | "场景转移成功"或"Invaild value of npc_name, it not Exists" | 返回的消息说明 |
| data | any | 否 | None | 对于这个请求，一般data项为空 |


接口名称：创建用户
接口路径(URL)：/user/create
请求方式：POST

请求参数 `UserCreateRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| name | str | 是 | 无 | 用户的名字 |
| sex | str | 是 | 无 | 用户的性别 |
| phone | str | 是 | 无 | 用户的电话 |
| money | int | 是 | 无 | 用户的货币或积分 |
| password | str | 是 | 无 | 用户的密码 |


接口响应数据：
响应方法 `response(data=user.to_dict())` 或 `response(message=f'user {req.name}, phone {req.phone} 已存在, 请勿重复创建')`

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，包括成功创建用户或用户已存在的提示 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含新创建用户所有信息的字典 |


接口名称：删除用户
接口路径(URL)：/user/remove
请求方式：POST

请求参数 `UserRemoveRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 是 | 无 | 指定要删除的用户的ID |

接口响应数据：
响应方法 `response(message=f'删除 user {req.id} 成功')`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，表明用户已成功删除 |
| data | any | 否 | None | 对于这个请求，一般data项为空 |


接口名称：查询用户
接口路径(URL)：/user/query
请求方式：POST

请求参数 `UserQueryRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 否 | None | 查询特定ID的用户 |
| name | str | 否 | None | 查询特定名字的用户 |
| order_by | str | 否 | {"id": False} | 排序依据和方式 |
| page | int | 否 | 1 | 需要查询的分页的页数 |
| limit | int | 否 | 10 | 每页返回的用户数量限制 |

接口响应数据：
响应方法 `response(data=json.dumps([user.to_dict() for user in users]))`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | []user | 否 | None | 返回的具体数据内容，是一个包含了查询到的所有符合条件的用户的信息列表 |


接口名称：更新用户信息
接口路径(URL)：/user/update
请求方式：POST

请求参数 `UserCreateRequest`：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| name | str | 是 | 无 | 用户的名字 |
| sex | str | 是 | 无 | 用户的性别 |
| phone | str | 是 | 无 | 用户的电话 |
| money | int | 是 | 无 | 用户的货币或积分 |
| id | str | 是 | 无 | 用户的 ID |

接口响应数据：
响应方法 `response(data=user.to_dict())`：
返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含用户所有信息的字典 |




# 数据库表结构设计

## 关系数据库

### NPC表

|   列名   |   数据类型         |  主键  | 默认值 | 唯一 | 外键 | 关系 |     描述     |
|---------|-----------------|--------|--------|-----|-----|----|--------------|
| id    | String(255)   |  是    |uuid.uuid4| 是  |    |    | NPC ID，uuid   |
| name  | String(64)    |  否    | None   | 否  |    |    | NPC名称       |
| short_description | String(255)| 否 | None | 否 |    |    | 短描述，主要用于前端展示 |
| trait   | Text           |  否    | None   | 否  |    |    | NPC特征，提示词内容 |
| prompt_description | Text  |  否    | None   | 否  |    |    | 提示词描述，存储完整提示词模板 |
| profile  | Text           |  否    | None   | 否  |    |    | 头像图片路径 |
| chat_background| Text   |  否    | None   | 否  |    |    | 聊天背景图片路径 |
| affinity_level_description| Text |  否 | None| 否 |  |  | 亲密度等级行为倾向描述 |
| knowledge_id  | String(255)  |  否 | None | 否  |    |    | 知识库的 index id |
| updated_at | DateTime  |  否    |datetime.now| 否 |    |   | 更新时间 |
| created_at | DateTime  |  否    |datetime.now| 否 |    |   | 创建时间 |

ORM设计：
```python
class NPC(Base):
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True) # NPC ID，uuid
    name = Column(String(64)) # NPC名称
    short_description = Column(String(255)) # 短描述，主要用于前端展示
    trait = Column(Text) #  NPC特征，提示词内容
    prompt_description = Column(Text) # 提示词描述，存储完整提示词模板
    profile = Column(Text) # 头像图片路径
    chat_background = Column(Text) # 聊天背景图片路径
    affinity_level_description = Column(Text) # 亲密度等级行为倾向描述
    knowledge_id = Column(String(255)) # 知识库的 index id
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now()) # 创建时间
    created_at = Column(DateTime, default=datetime.now())
```

### User表

|   列名   |   数据类型                  |  主键  | 默认值  | 唯一 | 外键 | 关系 |     描述     |
|---------|----------------------|--------|--------|------|----|----|-----------|
| id      | String(255)          |  是    |uuid.uuid4| 是  |    |    | 用户ID，自增id |
| name    | String(64)           |  否    | None   | 否   |    |    | 用户名称  |
| sex     | Enum("男", "女", "未知") |  否    | None   | 否   |    |    | 性别：男、女、未知 |
| phone   | String(11)           |  否    | None   | 否   |    |    | 手机号   |
| money   | Integer              |  否    | None   | 否   |    |    | 用户虚拟积分    |
| password| String(11)           |  否    | None   | 否   |    |    | 用户密码  |
| created_at | DateTime          |  否    | datetime.now| 否 |  |  | 创建时间  |

ORM设计：
```python
class User(Base):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True) # 用户ID，自增id
    name = Column(String(64)) # 用户名称 
    sex = Column(Enum("男", "女", "未知")) # 性别：男、女、未知
    phone = Column(String(11)) # 手机号
    money = Column(Integer) # 用户虚拟积分
    password = Column(String(11)) # 用户密码
    created_at = Column(DateTime, default=datetime.now()) # 创建时间
```

### Scene表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|-----|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |     |
| scene       | Text       | 否   | None   | 否  |     |    | 场景内容 |
| theater     | Text       | 否   | None   | 否  |     |    | 剧场名称 |
| theater_event | Text       | 否   | None   | 否  |     |    | 剧场事件 |
| roles       | String(255)| 否   | None   | 否  |     |    | 角色列表 |
| score       | String(255)| 否   | None   | 否  |     |    | 评分   |
| created_at  | DateTime   | 否   | datetime.now | 否 | |  | 创建时间 |

ORM设计：
```python
class Scene(Base):
    __tablename__ = 'scene'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    scene = Column(Text)
    theater = Column(Text)
    theater_event = Column(Text)
    roles = Column(String(255))
    score = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())
```

### NPC_User管理表

|      列名          |    数据类型    |  主键  | 默认值  | 唯一 |         外键          |  关系  |           描述           |
|-------------------|---------------|--------|--------|------|-----------------------|-------|-------------------------|
|       id           |  String(255)  |  是    |uuid.uuid4| 是  |                           |        |                          |
|      npc_id        |  String(255)  |  否    |  None   | 否   | ForeignKey('npc.id')  | NPC   | npc配置对象，外键      |
|     user_id        |  String(255)  |  否    |  None   | 否   | ForeignKey('user.id') | User  | 用户对象，外键         |
|      scene         |  String(255)  |  否    |  None   | 否   |                           |         | 场景描述                  |
|      score         |  Integer      |  否    |  None   | 否   |                           |         | 好感分数                 |
| affinity_level     |  Integer      |  否    |  None   | 否   |                           |         | 亲密度等级             |
|   created_at       |    DateTime   |  否    | datetime.now| 否 |                           |         | 创建时间                 |

ORM设计：
```python
class NPCUser(Base):
        # 表的名字
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # npc配置对象，外键
    # 通过关系关联NPCConfig对象
    npc = relationship('NPC')
    user_id = Column(String(255), ForeignKey('user.id'))  # 用户对象，外键
    # 通过关系关联User对象
    user = relationship('User')
    scene = Column(String(255))  # 场景描述
    score = Column(Integer)  # 好感分数
    affinity_level = Column(Integer)  # 亲密度等级
    created_at = Column(DateTime, default=datetime.now())  # 创建时间
```

### Event表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|------|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |  ID |
| npc_id      | String(255)| 否   | None | 否  | 是   | NPC | NPC对象，外键 |
| theater     | String(255)| 否   | None | 否  |     |    | 剧情章节 |
| theater_event | String(255)| 否 | None | 否  |     |    | 剧情的事件（JSON） |
| created_at  | DateTime   | 否   | datetime.now | 否 |     |    | 创建时间 |

ORM设计：
```python
class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # NPC对象，外键
    #关联NPC对象
    npc = relationship('NPC')
    theater = Column(String(255))  # 剧情章节
    theater_event = Column(String(255))  # 剧情的事件（JSON）
    created_at = Column(DateTime, default=datetime.now())  # 创建时间
```

### UserOpinion表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|------|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |  ID |
| labels      | String(255)| 否   | None | 否  |     |    | 意见标签（多标签通过逗号隔开） |
| name        | String(255)| 否   | None | 否  |     |    | 用户名称 |
| content     | Text       | 否   | None | 否  |     |    | 用户意见 |
| created_at  | DateTime   | 否   | datetime.now | 否 |     |    | 创建时间 |

ORM设计：
```python
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(Text)  # 用户意见
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

```

## 缓存数据库redis