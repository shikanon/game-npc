# coding:utf-8
import hashlib
from typing import List
from volcengine.maas import MaasService, MaasException, ChatRole
from elasticsearch7 import Elasticsearch

import gamenpc.utils.logger as logger

# 知识库中存储文本的字段
KG_FIELD_TEXT = "text"
KG_FIELD_VECTOR = "embedding"

class TextEmbeddingVector:
    def __init__(self, text, vector):
        self._text = text
        self._vector = vector
        self._id = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
    
    def set_id(self, id: str):
        self._id = id
    
    def get_id(self):
        return self._id
    
    def get_text(self):
        return self._text

    def get_vector(self):
        return self._vector
    
class KnowlegeResult:
    def __init__(self, score:float, content:str) -> None:
        self.score = score
        self.content = content
    
    def __str__(self)->str:
        return self.content

class MaaSKnowledgeEmbedding:
    def __init__(self, model, model_version) -> None:
        self.maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
        self.model = model
        self.model_version = model_version
        self.debug_logger = logger.DebugLogger(self.__class__.__name__)
    
    def encode(self, texts: List[str]) -> List[TextEmbeddingVector]:
        req = {
            "model": {
                "name": self.model,
                "version": self.model_version
            },
            "input": texts
        }
        self.debug_logger.debug(req)
        resp = self.maas.embeddings(req)
        result = []
        for i in range(len(texts)):
            emb = TextEmbeddingVector(texts[i], resp.data[i].embedding)
            result.append(emb)
        return result

class VectorDB:
    def __init__(self, url:str, table:str) -> None:
        pass
    
    def bulk_insert(self, data: List[TextEmbeddingVector]):
        pass

    def query(self):
        pass


class ESKnnVectorDB(VectorDB):
    def __init__(self, url:str, embedding: MaaSKnowledgeEmbedding) -> None:
        '''url: http://<用户名>:<密码>@<域名/ip地址>:<端口>
        table: vector存储表,
        '''
        self.debug_logger = logger.DebugLogger(self.__class__.__name__)
        self.embedding = embedding
        self.es = Elasticsearch(
            hosts=[url],
            verify_certs=False, 
        )
        self.table = "knowledge"
        self.init_db(self.table)
    
    def init_db(self, table:str):
        '''初始化表
        '''
        self.table = table
        if not self.es.indices.exists(self.table):
            self.es.indices.create(
                index=self.table,
                body={
                    "mappings": {
                        "properties": {
                            KG_FIELD_TEXT: { "type": "text" },
                            KG_FIELD_VECTOR: { "type": "knn_vector", "dimension": 1024 }
                        }
                    },
                    "settings": {
                        "index": {
                            "refresh_interval": "1s",
                            "knn": True,
                            "knn.space_type": "cosinesimil",
                            "number_of_replicas": "1"
                        }
                    }
                }
            )
            self.debug_logger.debug("成功创建index: %s"%self.table)
        else:
            self.debug_logger.debug("index已经存在: %s"%self.table)

    def query(self, text: str):
        """查询给定文本的最匹配的知识。
        
        参数:
            text (str): 需要匹配的文本。
        
        返回:
            给定文本的最匹配的知识。
        """
        return self.query_topk(text, topk=1, score=0.1)

    def query_topk(self, text: str, topk:int, score:float):
        '''查询给定文本的前k个匹配知识。
        
        参数:
            text (str): 需要匹配的文本。
            topk (int): 需要返回的最佳匹配结果数量。
            score (float): 返回的匹配结果的最小相似度得分。
        
        返回:
            给定文本的前k个匹配知识。
        '''
        vectors = self.embedding.encode([text])
        return self.query_topk_vector(vectors[0], topk, score)

    def query_topk_vector(self, vector:TextEmbeddingVector, topk:int, score:float):
        """查询给定向量knn算法下最相近的k个向量
        
        参数:
            vector (TextEmbeddingVector): 需要匹配的向量。
            topk (int): 需要返回的最佳匹配结果数量。
            score (float): 返回的匹配结果的最小相似度得分。

        返回:
            knn算法下最相近的k个向量结果
        
        """
        es_res = self.es.search(
            body={
                "size": topk,
                "query": {
                    "knn": {
                        KG_FIELD_VECTOR: {
                            "vector": vector.get_vector(), 
                            "k": 1
                            }
                        }
                    },
                "_source": ["text"],
            },
            index=self.table,
        )
        self.debug_logger.debug(es_res)
        result = []
        for hit in es_res['hits']['hits']:
            if hit["score"] > score:
                result.append(KnowlegeResult(hit["score"], hit["_source"]))
        return result
    
    def bulk_insert(self, data: List[str])->None:
        vectors = self.embedding.encode(texts=data)
        self.bulk_insert_vector(vectors)

    def bulk_insert_vector(self, vectors: List[TextEmbeddingVector])->None:
        data = []
        for tv in vectors:
            # 确保写入唯一id
            data.append({"index": {"_index": self.table, "_id": tv.get_id()}})
            # 写入数据
            data.append({
                KG_FIELD_TEXT: tv.get_text(),
                KG_FIELD_VECTOR: tv.get_vector(),
            })
        self.debug_logger.debug(data)
        self.es.bulk(data)
    
    def insert(self, id:str, text:str):
        vectors = self.embedding.encode(texts=[text])
        self.insert_vector(id=id, vector=vectors[0])
    
    def insert_vector(self, id:str, vector: TextEmbeddingVector):
        doc = {
            KG_FIELD_TEXT: vector.get_text(),
            KG_FIELD_VECTOR: vector.get_vector(), 
        }
        self.es.create(index=self.table, id=id, body=doc)
    
    def update(self, id:str, text:str):
        vectors = self.embedding.encode(texts=[text])
        self.update_vector(id=id, vector=vectors[0])
    
    def update_vector(self, id:str, vector:TextEmbeddingVector):
        doc = {
            "doc": {
                KG_FIELD_TEXT: vector.get_text(),
                KG_FIELD_VECTOR: vector.get_vector(),
            }
        }
        self.es.update(self.table, id=id,body=doc)

    def delete_all(self):
        self.es.delete_by_query(
            index=self.table,
            body={
                "query": {
                    "match_all": {}
                }
            }
        )
        self.debug_logger.debug("完成数据表(%s)的数据删除工作"%self.table)
    
    def delete_by_id(self, id):
        self.es.delete(index=self.table, id=id)


