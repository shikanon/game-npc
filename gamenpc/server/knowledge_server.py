# coding:utf-8
"""
doubao chat wrapper.
author: shikanon
create: 2024/1/8
"""
import json
import os
from fastapi import FastAPI, File, HTTPException
from pydantic import BaseModel
from typing import List

from gamenpc.utils import logger
from gamenpc.memory import knowledge

# web 应用服务
app = FastAPI()
debuglog = logger.DebugLogger("chat bot web")

# 知识库初始化
emb = knowledge.MaaSKnowledgeEmbedding(model="bge-large-zh", model_version="1.0")
kg_db = knowledge.ESKnnVectorDB(os.environ.get("ES_URL"), emb)
kg_db.init_db("klbq")


# 请求数据模型
class TextQuery(BaseModel):
    text: str

class InsertQuery(BaseModel):
    id: str
    text: str

class QueryTopKRequest(BaseModel):
    text: str
    topk: int
    score: float

class BulkInsertRequest(BaseModel):
    data: List[str]

@app.post("/query/")
async def query(text_query: TextQuery):
    try:
        result = kg_db.query(text_query.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/insert/")
async def api_insert(insert_query: InsertQuery):
    try:
        kg_db.insert(insert_query.id, insert_query.text)
        return {"message": "Insert successful."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 查询Top K API
@app.post("/query_topk/")
async def api_query_topk(request: QueryTopKRequest):
    objs = kg_db.query_topk(request.text, request.topk, request.score)
    result = {}
    for i in range(len(objs)):
        result[i] = objs[i].content
    return result

# 批量插入API
@app.post("/bulk_insert/")
async def api_bulk_insert(request: BulkInsertRequest):
    try:
        kg_db.bulk_insert(request.data)
        return {"message": "Bulk insert successful."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)