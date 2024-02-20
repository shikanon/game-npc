# coding:utf-8
"""
doubao chat wrapper.
author: shikanon
create: 2024/1/8
"""
import json
import os
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from langchain.pydantic_v1 import Field
from fastapi.responses import PlainTextResponse
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts.chat import HumanMessagePromptTemplate

from gamenpc.model import doubao
from gamenpc.utils import logger
from gamenpc.memory import knowledge

# web 应用服务
app = FastAPI()
debuglog = logger.DebugLogger("chat bot web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 知识库初始化
emb = knowledge.MaaSKnowledgeEmbedding(model="bge-large-zh", model_version="1.0")
kg_db = knowledge.ESKnnVectorDB(os.environ.get("ES_URL"), emb)

# 回调函数类
fn = doubao.ModelFunctionClass(
    name="CallHumanCustomerService",
    description="""当需要转人工服务的时候使用此函数。当你觉得无法很好帮助客户解决问题，
    需要借助专业人士的力量，你可以使用此函数方法转到的人工客服，这个函数的输入question是你基于上下文总结归纳的用户问题和描述""",
    parameters={
        "properties": {
            "question": {"description": "用户咨询的问题和问题相关的上下文信息", "type":"string"}
            },
            "required": ["question"],
            "type": "object",
    },
)

chat = doubao.ChatSkylark(
    model="skylark2-pro-4k",
    model_version="1.100",
    model_endpoint="mse-20231227193502-58xhk",
    top_k=1,
    functions=[fn]
    )

# 回调函数具体实现，当大模型判断使用 CallHumanCustomerService 的时候会回调这个函数
def CallHumanCustomerService(question: str):
    return "连接上10号客服...用户的问题是：%s"%question

system_prompt = "你是一位智能游戏客服，礼貌且善于洞察客户情绪。你的主要职责是帮助客户解决他们在游戏中遇到的问题。"

with open("gamenpc/template/game-customer-service.template","r",encoding="utf-8") as fr:
    character_prompt_template = fr.read()


class QuestionRequest(BaseModel):
    '''
    question: 问题，文本格式
    question_type: 问题类型，文本格式
    history_messages: 采用问题答案对[{"类型":"问题1"},{"类型":"答案1"},{"类型":"问题1"}]，类型两种：AI和Human
    session_id: 会话id，整形，用来缺乏是否同一个会话上下文
    '''
    question: str
    question_type: str = "knowledge"
    history_messages: List[Dict[str,str]]
    session_id: int = 0

class FAQRequest(BaseModel):
    '''
    faq_id: 问答的id索引
    question: 问题
    answer: 答案
    faq_type: 类型
    '''
    faq_id: str
    question: str
    answer: str
    faq_type: str

class TemplateRequest(BaseModel):
    template_id: int
    template: str


def get_knowledge_content(req: QuestionRequest):
    """
    该函数用于获取知识库的内容，函数采用问题和历史消息构建context_question，然后使用ES进行查询，输出结果最接近问题的内容。
    
    输入参数:
    req: QuestionRequest对象，包含问题，历史消息和问题类型等信息
    """
    if len(req.history_messages)>0:
        context_question = "/n".join([r[0]+r[1] for r in req.history_messages]) + req.question
    else:
        context_question = req.question
    if req.question_type != "knowledge" or req.question_type != "":
        kg_db.init_db(req.question_type)
    else:
        kg_db.init_db("knowledge")
    similar_content = kg_db.query(context_question)
    debuglog.debug(similar_content)
    return similar_content

# 知识问答接口
@app.post("/ask")
async def ask_question(req: QuestionRequest):
    '''该函数用于处理用户的问题并生成回答，同时维护历史消息记录。
    '''
    # 这里应该是问题解析和回答的逻辑
    messages = [
        SystemMessage(content=system_prompt),
    ]

    # 将历史聊天记录的上下文拼接进来
    for m in req.history_messages:
        if "Human" in m:
            messages.append(HumanMessage(content=m["Human"]))
        if "AI" in m:
            messages.append(AIMessage(content=m["AI"]))
    query_result = get_knowledge_content(req)
    knowledge_prompt = HumanMessagePromptTemplate.from_template(
                template=character_prompt_template,
            ).format(knowledge=query_result, question=req.question)
    debuglog.debug(knowledge_prompt)
    messages.append(knowledge_prompt)
    # 将上下文拼接后访问大模型
    result = chat(messages)
    if "function_call" in result.additional_kwargs:
        fn_name = result.additional_kwargs["function_call"]["name"]
        fn_params = result.additional_kwargs["function_call"]["arguments"]
        params = json.loads(fn_params)
        print(fn_name)
        print(params)
        answer = globals()[fn_name](**params) + result.content
    else:
        answer = result.content
    debuglog.debug(messages)
    debuglog.debug(answer)
    return {"question": req.question, "answer": answer, "history": req.history_messages, "context": messages}

# 知识问答接口
@app.post("/ask-stream")
async def ask_question_sse(req: QuestionRequest):
    '''该函数用于处理用户的问题并生成回答，同时维护历史消息记录。
    '''
    # 这里应该是问题解析和回答的逻辑
    messages = [
        SystemMessage(content=system_prompt),
    ]

    # 将历史聊天记录的上下文拼接进来
    for m in req.history_messages:
        if "Human" in m:
            messages.append(HumanMessage(content=m["Human"]))
        if "AI" in m:
            messages.append(AIMessage(content=m["AI"]))
    query_result = get_knowledge_content(req)
    knowledge_prompt = HumanMessagePromptTemplate.from_template(
                template=character_prompt_template,
            ).format(knowledge=query_result, question=req.question)
    debuglog.debug(knowledge_prompt)
    messages.append(knowledge_prompt)
    # 将上下文拼接后访问大模型
    result = chat.astream(messages)
    return StreamingResponse(chat.astream(messages), media_type="text/event-stream")


# 直接上传FAQ到知识库
@app.post("/save-faq/")
async def save_faq(req: FAQRequest):
    '''该函数用于处理FAQ。
    faq_id: 问答的id索引
    question: 问题
    answer: 答案
    faq_type: 类型
    '''
    # 这里应该是文件内容的解析逻辑
    content = "question: %s \n\n answer: %s"%(req.question, req.answer)
    if len(content) > 500:
        return {"error": "FAQ的内容太长了，大模型context容纳不下"}
    if req.faq_type != "knowledge" or req.faq_type !="":
        kg_db.init_db(req.faq_type)
    else:
        kg_db.init_db("knowledge")
    kg_db.insert(id=req.faq_id, text=content)
    return {"faq_id": req.faq_id, "content": content}

# 加载模板
@app.post("/load-template/")
async def load_template(req: TemplateRequest):
    global character_prompt_template
    if "{knowledge}" in req.template and "{question}" in req.template:
        character_prompt_template = req.template
        return {"status": "success"}
    else:
        return {"status": "faild"}


@app.delete("/delete-faq-by-id/{faq_id}")
async def delete_faq_by_id(faq_id:str):
    try:
        kg_db.delete_by_id(id=faq_id)
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": e}


# 文件上传解析接口
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    '''该函数用于处理用户上传的文件并解析内容。
    '''
    # 这里应该是文件内容的解析逻辑
    parsed_content = "这是解析后的内容示例。"
    content = await file.read()
    kg_unit = content.decode('utf-8').split("/n")
    debuglog.debug(len(kg_unit))
    kg_db.bulk_insert(kg_unit)
    return {"filename": file.filename, "content": kg_unit}

# 知识问答Debug接口
@app.post("/debug-ask")
async def debug_ask_question(req: QuestionRequest):
    '''该函数用于处理用户的问题并生成回答，同时维护历史消息记录。'''
    # 这里是知识问答的调试逻辑
    debug_info = "这是调试信息的示例。"
    similar_content = get_knowledge_content(req)
    return {"query": similar_content}

# websocket的方式进行回复
@app.websocket("/ws-chatbot")
async def websocket_endpoint(websocket: WebSocket):
    chat = doubao.ChatSkylark(
        model="skylark2-pro-4k",
        model_version="1.100",
        model_endpoint="mse-20231227193502-58xhk",
        top_k=1,
        streaming=True,
    )
    await websocket.accept()
    history = []
    while True:
        hunman_ask_data = await websocket.receive_text()
        messages = history
        messages.append(HumanMessage(content=hunman_ask_data))
        print(messages)
        print(hunman_ask_data)
        answer = ""
        async for chunk in chat.astream(hunman_ask_data):
            print(chunk)
            if chunk.content == '':
                continue
            await websocket.send_text(chunk.content)
            answer = answer + chunk.content
        websocket.send_text('/n')
        history.append(HumanMessage(content=hunman_ask_data))
        history.append(AIMessage(content=answer))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
