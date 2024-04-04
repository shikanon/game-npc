# 接口文档

### NPC聊天接口
接口路径(URL)：/npc/chat
请求方式：POST

接口请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|------------------|
| user_id | str      | 是 | 无 | 用户ID |
| npc_id  | str      | 是 | 无 | NPC的ID |
| scene   | str      | 是 | 无 | 场景 |
| question| str      | 是 | 无 | 用户问题 |
| content_type | str | 是 | 无 | 内容类型 |

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

---------------------------------------------------------------------------------------

### NPC聊天调试接口
接口路径(URL)：/npc/debug_chat
请求方式：POST

接口请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|------------------|
| user_id | str      | 是 | 无 | 用户ID |
| npc_id  | str      | 是 | 无 | NPC的ID |
| scene   | str      | 是 | 无 | 场景 |
| question| str      | 是 | 无 | 用户问题 |
| content_type | str | 是 | 无 | 内容类型 |

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
| dialogue_context | str | 是 | 无 | 聊天上下文：[]dialogue |

---------------------------------------------------------------------------------------

### 获取用户的聊天对象NPC信息
接口路径(URL)：/npc/get_npc_users
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| user_id | str      | 是 | 无 | 用户ID |
| npc_id  | str      | 是 | 无 | NPC的ID |
| order_by| str      | 否 | "desc" | 排序方式，desc表示降序，asc表示升序 |
| page    | int      | 否 | 0 | 分页查询的页码，从0开始 |
| limit   | int      | 否 | 1 | 每页的数量 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code    | int  | 是 | 0 | 响应状态码，0表示执行成功，-1表示查询内容不存在 |
| msg     | str  | 是 | "执行成功"或“Invaild value of npc_id, it not Exists” | 返回的消息说明 |
| data    | []npc_user  | 否 | None | 返回的具体数据内容，这里是NPC的详细信息 |

---------------------------------------------------------------------------------------

### 获取用户的聊天对象NPC完整信息
接口路径(URL)：/npc/get_npc_all_info
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| user_id | str      | 是 | 无 | 用户ID |
| npc_id  | str      | 是 | 无 | NPC的ID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code    | int  | 是 | 0 | 响应状态码，0表示执行成功，-1表示查询内容不存在 |
| msg     | str  | 是 | "执行成功"或“Invaild value of npc_id, it not Exists” | 返回的消息说明 |
| data    | []info  | 否 | None | 返回的具体数据内容，这里是NPC的详细信息 |

info的格式：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| id    | int  | 是 | 0 |主键 |
| npc_id     | str  | 是 | None | npc配置对象，外键 |
| user_id    | str  | 否 | None | 用户对象，外键 |
| name    | str  | 是 | 0 | None| npc名称 |
| scene     | str  | 是 | None| 场景描述 |
| score    | int  | 否 | None | 好感分数 |
| trait    | istrnt  | 是 | 0 | NPC特征，提示词内容 |
| affinity_level_description     | str  | 是 | None| 亲密度等级描述 |
| short_description    | str  | 否 | None | 短描述 |
| prompt_description    | str  | 是 | None | 泼墨体 |
| profile     | str  | 是 | None| 头像 |
| chat_background    | str  | 否 | None | 聊天背景图 |
| dialogue_context    | []dialogue  | 否 | None | 聊天上下文 |

dialogue的格式：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| id    | str  | 是 | 0 |主键 |
| role_from     | str  | 是 | None | 内容发出对象ID |
| role_to    | str  | 否 | None | 内容发送对象ID |
| content    | str  | 是 | 0 | None| 内容 |
| content_type     | str  | 是 | None| 内容类型 |
| created_at    | str  | 否 | None | 时间 |
---------------------------------------------------------------------------------------

### 获取NPC历史对话
接口路径(URL)：/npc/get_history_dialogue
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_id | str | 是 | 无 | NPCID |
| user_id | str | 是 | 无 | 用户ID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|----------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg | str | 是 | "执行成功"或"NPC not found" | 返回的消息说明 |
| data | []dialogue | 否 | None | 返回的具体数据内容，这里是NPC的历史对话 |

dialogue的格式：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| id    | str  | 是 | 0 |主键 |
| role_from     | str  | 是 | None | 内容发出对象ID |
| role_to    | str  | 否 | None | 内容发送对象ID |
| content    | str  | 是 | 0 | None| 内容 |
| content_type     | str  | 是 | None| 内容类型 |
| created_at    | str  | 否 | None | 时间 |
---------------------------------------------------------------------------------------

### 重置NPC历史对话
接口路径(URL)：/npc/clear_history_dialogue
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_id | str | 是 | 无 | NPCID |
| user_id | str | 是 | 无 | 用户ID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|--------------------|----------|--------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg  | str | 是 | "记忆、好感重置成功!"或"NPC not found" | 返回的消息说明 |

---------------------------------------------------------------------------------------

### 创建NPC
接口路径(URL)：/npc/create
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| name | str | 是 | 无 | NPC的名字 |
| trait | str | 是 | 无 | NPC的性格特点 |
| sex | int | 是 | 无 | NPC的性别 |
| short_description | str | 否 | "" | NPC的简短描述 |
<!-- | prompt_description | str | 是 | 无 | NPC的提示描述 | -->
| profile | str | 是 | 无 | NPC的个人资料 |
| chat_background | str | 是 | 无 | NPC的聊天背景 |
| affinity_level_description | str | 是 | 无 | NPC的亲和级别描述 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | npc | 否 | None | 返回的具体数据内容，是一个包含新创建NPC所有信息的字典 |

---------------------------------------------------------------------------------------

### 查询NPC
接口路径(URL)：/npc/query
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| name | str | 否 | None | 过滤条件，NPC的名称 |
| page | int | 否 | 1 | 请求的页数 |
| limit | int | 否 | 10 | 每页返回结果的数量 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | data | 否 | None | 返回的具体数据内容 |

data的结构如下：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| total | int | 是 | 0 | 返回的数据总量 |
| list | []npc | 是 | None | 返回的数据列表 |

---------------------------------------------------------------------------------------

### 获取单个NPC
接口路径(URL)：/npc/get
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| id | str | 是 | 无 | NPCID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | npc | 否 | None | 返回的具体数据内容 |

---------------------------------------------------------------------------------------

### 更新NPC
接口路径(URL)：/npc/update
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| name | str | 是 | 无 | NPC的名字 |
| trait | str | 是 | 无 | NPC的性格特点 |
| sex | int | 是 | 无 | NPC的性别 |
| short_description | str | 否 | "" | NPC的简短描述 |
<!-- | prompt_description | str | 是 | 无 | NPC的提示描述 | -->
| profile | str | 是 | 无 | NPC的个人资料 |
| chat_background | str | 是 | 无 | NPC的聊天背景 |
| affinity_level_description | str | 是 | 无 | NPC的亲和级别描述 |
| status    | int  | 否 | None | 发布状态，0: Unknown 未知, 1: Save 待发布, 2: Publish 已发布 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |
| data | npc | 否 | None | 返回的具体数据内容，是一个包含新创建NPC所有信息的字典 |

---------------------------------------------------------------------------------------

### 更新NPC角色状态
接口路径(URL)：/npc/update_status
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------------------|
| id | str | 是 | 无 | NPC ID |
| status    | int  | 否 | None | 发布状态，0: Unknown 未知, 1: Save 待发布, 2: Publish 已发布 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------------------------|
| code | int | 是 | 0 | 响应状态码，0表示执行成功 |
| msg | str | 是 | "执行成功" | 返回的消息说明 |

---------------------------------------------------------------------------------------

### 删除NPC
接口路径(URL)：/npc/remove
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 是 | 无 | 指定要删除的NPC的ID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，表明用户已成功删除 |

---------------------------------------------------------------------------------------

### 切换场景
接口路径(URL)：/npc/shift_scenes
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------|
| npc_id | str | 是 | 无 | NPCID |
| user_id | str | 是 | 无 | 用户ID |
| scene | str | 是 | 无 | 要切换的场景 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|--------------------|----------|--------|------------------|
| code | int | 是 | 0或400 | 响应状态码，0表示执行成功，400表示NPC未找到 |
| msg  | str | 是 | "场景转移成功"或"Invaild value of npc_name, it not Exists" | 返回的消息说明 |

---------------------------------------------------------------------------------------

### 上传文件
接口路径(URL)：/npc/file_upload
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| file | File | 是 | 是 | 用户的 ID |
| image_type | int | 是 | 是 | 文件类型：0: Unknown 未知，1: Avatar 头像，2: ChatBackground 聊天背景 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | url | 是 | None | 返回的具体数据内容，文件的url |

---------------------------------------------------------------------------------------

### 用户注册
接口路径(URL)：/user/register
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| name | str | 是 | 是 | 用户的名字 |
| sex | int | 是 | 无 | 用户的性别 |
| phone | str | 是 | 无 | 用户的电话 |
| password | str | 是 | 是 | 用户的密码 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，包括成功创建用户或用户已存在的提示 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含新创建用户所有信息的字典 |

---------------------------------------------------------------------------------------

### 用户登录
接口路径(URL)：/user/login
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| name | str | 是 | 是 | 用户的名字 |
| password | str | 是 | 是 | 用户的密码 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，包括成功创建用户或用户已存在的提示 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含新创建用户所有信息的字典 |

---------------------------------------------------------------------------------------

### 删除用户
接口路径(URL)：/user/remove
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 是 | 无 | 指定要删除的用户的ID |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明，表明用户已成功删除 |

---------------------------------------------------------------------------------------

### 查询用户
接口路径(URL)：/user/get
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 否 | None | 查询特定ID的用户 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|-------------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含了查询到的所有符合条件的用户的信息列表 |

---------------------------------------------------------------------------------------

### 更新用户信息
接口路径(URL)：/user/update
请求方式：POST

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| id | str | 是 | 是 | 用户的 ID |
| name | str | 是 | 无 | 用户的名字 |
| sex | int | 是 | 无 | 用户的性别 |
| phone | str | 是 | 无 | 用户的电话 |
| password | str | 是 | 无 | 用户密码 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | user | 否 | None | 返回的具体数据内容，是一个包含用户所有信息的字典 |

### 生成角色描述
接口路径(URL)：/tools/generator_npc_trait
请求方式：GET

请求参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|---------------------------------|
| npc_name | str | 是 | 无 | npc的名字 |
| npc_sex | str | 是 | 无 | npc的性别,"男"或"女" |
| npc_short_description | str | 是 | 无 | npc的简短描述 |

返回参数：
| 字段名称 | 数据类型 | 是否必须 | 默认值 | 描述 |
|---------|----------|----------|--------|--------------------------------|
| code | int | 是 | 无 | 响应状态码，0表示执行成功 |
| msg | str | 是 | 无 | 返回的消息说明 |
| data | str | 是 | None | 返回生成的提示词的具体内容 |


# 数据库表结构设计

## 关系数据库

### NPC表

|   列名   |   数据类型         |  主键  | 默认值 | 唯一 | 外键 | 关系 |     描述     |
|---------|-----------------|--------|--------|-----|-----|----|--------------|
| id    | String(255)   |  是    |uuid.uuid4| 是  |    |    | NPC ID，uuid   |
| name  | String(64)    |  否    | None   | 否  |    |    | NPC名称       |
| short_description | String(255)| 否 | None | 否 |    |    | 短描述，主要用于前端展示 |
| trait   | Text           |  否    | None   | 否  |    |    | NPC特征，提示词内容 |
| sex   | Integer           |  否    | None   | 否  |    |    | NPC性别 |
| prompt_description | Text  |  否    | None   | 否  |    |    | 提示词描述，存储完整提示词模板 |
| profile  | Text           |  否    | None   | 否  |    |    | 头像图片路径 |
| chat_background| Text   |  否    | None   | 否  |    |    | 聊天背景图片路径 |
| affinity_level_description| Text |  否 | None| 否 |  |  | 亲密度等级行为倾向描述 |
| knowledge_id  | String(255)  |  否 | None | 否  |    |    | 知识库的 index id |
| status  | String(255)  |  否 | None | 否  |    |    | 发布状态，0: Unknown 未知, 1: Save 待发布, 2: Publish 已发布 |
| updated_at | DateTime  |  否    |datetime.now| 否 |    |   | 更新时间 |
| created_at | DateTime  |  否    |datetime.now| 否 |    |   | 创建时间 |

ORM设计：
```python
class NPC(Base):
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    short_description = Column(String(255))
    trait = Column(Text)
    sex = Column(Integer)
    prompt_description = Column(Text)
    profile = Column(Text)
    chat_background = Column(Text)
    affinity_level_description = Column(Text)
    status = Column(Integer)
    knowledge_id = Column(String(255))
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = Column(DateTime, default=datetime.now())
```

### User表

|   列名   |   数据类型                  |  主键  | 默认值  | 唯一 | 外键 | 关系 |     描述     |
|---------|----------------------|--------|--------|------|----|----|-----------|
| id      | String(255)          |  是    |uuid.uuid4| 是  |    |    | 用户ID，自增id |
| name    | String(64)           |  否    | None   | 否   |    |    | 用户名称  |
| sex     | Integer              |  否    | None   | 否   |    |    | 性别：0: 未知, 1: 男, 2: 女 |
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
|       id           |  String(255) |  是    |uuid.uuid4| 是  |                       |         |                      |
|      npc_id        |  String(255) |  否    |  None   | 否   | ForeignKey('npc.id')  | NPC     | npc配置对象，外键      |
|     user_id        |  String(255) |  否    |  None   | 否   | ForeignKey('user.id') | User    | 用户对象，外键         |
|      name          |  String(255) |  否    |  None   | 否   |                       |         | 场景描述              |
|      scene         |  String(255) |  否    |  None   | 否   |                       |         | 场景描述              |
|      score         |  Integer     |  否    |  None   | 否   |                       |         | 好感分数              |
|     trait          |  Text        |  否    |  None   | 否   |                       |         | NPC特征，提示词内容 |
| affinity_level     |  Text        |  否    |  None   | 否   |                       |         | 亲密度等级描述         |
|   created_at       |  DateTime    |  否    | datetime.now| 否 |                     |         | 创建时间              |

ORM设计：
```python
class NPCUser(Base):
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # npc配置对象，外键
    # 通过关系关联NPCConfig对象
    npc = relationship('NPC')
    user_id = Column(String(255), ForeignKey('user.id'))  # 用户对象，外键
    # 通过关系关联User对象
    user = relationship('User')
    name = Column(String(255))  # NPC名称
    scene = Column(String(255))  # 场景描述
    trait = Column(Text)  # 场景描述
    score = Column(Integer)  # 好感分数
    affinity_level = Column(Text)  # 亲密度等级
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