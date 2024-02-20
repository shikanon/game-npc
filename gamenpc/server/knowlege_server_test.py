from fastapi.testclient import TestClient
from knowledge_server import app  # 假设API接口定义在名为main.py的文件中

client = TestClient(app)

def test_query():
    # 测试查询接口
    response = client.post("/query/", json={"text": "测试文本"})
    assert response.status_code == 200
    # 这里应该添加更多的断言来检查返回值的内容

def test_insert():
    # 测试插入接口
    response = client.post("/insert/", json={"id": "123", "text": "测试文本"})
    assert response.status_code == 200
    assert response.json() == {"message": "Insert successful."}

def test_query_topk():
    # 测试查询topk接口
    response = client.post("/query_topk/", json={"text": "测试文本", "topk": 5, "score": 0.1})
    assert response.status_code == 200
    # 这里应该添加更多的断言来检查返回值的内容

def test_bulk_insert():
    # 测试批量插入接口
    response = client.post("/bulk_insert/", json={"data": ["测试文本1", "测试文本2"]})
    assert response.status_code == 200
    assert response.json() == {"message": "Bulk insert successful."}


# 如果使用pytest来执行测试，你可以在命令行运行：
# pytest knowlege_server_test.py