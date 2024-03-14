# test_main.py

from fastapi.testclient import TestClient
from gamenpc.webserver import app
import json

client = TestClient(app)

# 测试创建用户
def test_create_user():
    payload = {
        "name": "TestUser1",
        "sex": "male",
        "phone": "12345678901",
        "money": 100,
        "password": "password123"
    }
    response = client.post("/user/create", json=payload)
    assert response.status_code == 200
    resp_data = response.json()
    print(resp_data)

# 测试查询用户
# def test_query_user():
#     query = {
#         "id": "1",
#         "name": "",
#         "order_by": "desc",
#         "page": 0,
#         "limit": 1
#     }
#     response = client.get("/user/query", params=query)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)


# # 测试赞美NPC
# def test_create_npc():
#     payload = {
#         "name": "NPC1",
#         "trait": "friendly",
#         "short_description": "A friendly npc",
#         "prompt_description": "NPC seems friendly",
#         "profile": "friendly.png",
#         "chat_background": "chat_bg.png",
#         "affinity_level_description": "High affinity",
#     }
#     response = client.post("/npc/create", json=payload)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)


# # 测试NPC查询
# def test_query_npc():
#     data = {
#         "id": "1",
#         "name": "NPC1",
#         "order_by": "desc",
#         "page": 0,
#         "limit": 1
#     }
#     response = client.get("/npc/query", params=data)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)

# # 测试切换场景
# def test_shift_scenes():
#     payload = {
#         "npc_user_id": "1",
#         "scene": "battlefield",
#     }
#     response = client.post("/npc/shift_scenes", json=payload)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)

# # 测试NPC对话
# def test_chat():
#     payload = {
#         "id": "1",
#         "user_id": "1",
#         "npc_id": "1",
#         "scene": "battlefield",
#         "question": "What's your name?",
#         "contentType": "text",   
#     }
#     response = client.post("/npc/chat", json=payload)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)

# # 测试获取历史对话
# def test_get_history_dialogue():
#     query = {
#         "npc_user_id": "1"
#     }
#     response = client.get("/npc/get_history_dialogue", params=query)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)

# # 测试文件上传
# def test_upload_file():
#     filepath = './test.txt'
#     files = { 'file': open(filepath, 'r') }
#     response = client.post("/file/upload", files=files)
#     assert response.status_code == 200
#     resp_data = response.json()
#     print(resp_data)