# coding:utf-8
import os
import logging
import time
from elasticsearch7 import Elasticsearch
import knowledge


logging.basicConfig(level=logging.DEBUG)

es_url = os.environ.get("ES_URL")
print("es url:",es_url)
es_table = "knowledge_test"
emb = knowledge.MaaSKnowledgeEmbedding(model="bge-large-zh", model_version="1.0")
db = knowledge.ESKnnVectorDB(es_url, emb)
db.init_db(es_table)
db.delete_all()
time.sleep(2)

def test_bulk_insert():
    with open("Readme.md", "r", encoding="utf-8") as fr:
        doc = fr.read()
    kg_unit = doc.split("/n")
    print(len(kg_unit))
    db.bulk_insert(kg_unit)
    time.sleep(2)


def test_insert_update_query():
    db.insert(id="123", text="gocanvas是一个golang封装的3D模型动画演示库，提供了gltf、obj、fbx等多种模型格式加载，支持天空盒、灯光和脚本动画编辑等功能。")
    time.sleep(1)
    print(db.query("gocanvas是什么？"))
    db.update(id="123", text="gocanvas是shikanon写的一个3D模型动画演示库。")
    time.sleep(2)
    print(db.query("gocanvas是什么？"))
    db.delete_by_id(id="123")