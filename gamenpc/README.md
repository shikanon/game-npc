# 接口文档

## Chat接口
该接口允许用户通与NPC进行聊天。

方法：POST api/chat

**请求**
发送至该接口的请求体必须符合`ChatRequest`模型的格式，并包含以下字段：
- `user_name`: string — 用户名称。
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。
- `question`: string — 用户提出的问题，以文本形式提供。

**响应格式**
接口将返回一个包含以下字段的JSON对象：
answer: string — 来自NPC的回答。
affinity_score: int — 表示用户与NPC之间亲密度分数。
thought: string — NPC的思考上下文信息。


## 设置 NPC 信息接口

方法：POST /api/npc/set_config

**请求**
发送至该接口的请求体必须符合`NPCConfigRequest`模型的格式，并包含以下字段：
- `user_name`: string — 用户名称。
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。
- `trait`: string — NPC的特征。

**响应格式**
接口将返回一个包含以下字段的JSON对象：
id: string — NPC的唯一ID。
name: int — NPC名称，该值用于确定和哪个NPC交互。
userName: string — 用户名称。
trait: string — NPC的特征。
score: string — 好感分数。
affinity_level: string — 好感度等级。

## 查询 NPC 信息接口

方法：GET /api/npc/get_all_config

**请求**
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。

**响应格式**
接口将返回一个包含以下字段的JSON对象的列表：
id: string — NPC的唯一ID。
name: int — NPC名称，该值用于确定和哪个NPC交互。
userName: string — 用户名称。
trait: string — NPC的特征。
score: string — 好感分数。
affinity_level: int — 好感度等级。


## 查询 NPC 信息接口

方法：GET /api/npc/get_my_config

**请求**
- `user_name`: string — 用户名称。
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。

**响应格式**
接口将返回一个包含以下字段的JSON对象：
id: string — NPC的唯一ID。
name: int — NPC名称，该值用于确定和哪个NPC交互。
userName: string — 用户名称。
trait: string — NPC的特征。
score: string — 好感分数。
affinity_level: int — 好感度等级。


## 清除 NPC 记忆接口

方法：GET /api/npc/clear_memory

**请求**
- `user_name`: string — 用户名称。
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。

**响应格式**
接口将返回一个包含以下字段的JSON对象：
status: string — 状态。
message: int — 执行信息。


## 转换场景，提供场景转换能力接口

方法：POST /api/npc/shift_scenes

**请求**
- `user_name`: string — 用户名称。
- `npc_name`: string — NPC名称，该值用于确定和哪个NPC交互。
- `scene`: string — 场景。

**响应格式**
接口将返回一个包含以下字段的JSON对象：
status: string — 状态。
message: int — 执行信息。


## 加载和丰富NPC的知识库接口

方法：POST /api/npc/load-knowlege