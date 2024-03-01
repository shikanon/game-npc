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

## clear 接口

清楚 NPC 记忆，重置

方法：POST api/npc/clear_memory

## npc-info 接口

查询 NPC 信息


## load-knowlege 接口

加载和丰富NPC的知识库

方法：POST api/npc/load-knowlege

## shift-scenes 接口

转换场景，提供场景转换能力
