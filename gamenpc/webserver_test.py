# test_main.py

from fastapi.testclient import TestClient
from gamenpc.webserver import app

client = TestClient(app)

def test_chat():
    # 假设的测试username
    test_user_name = "啊彬"
    test_npc_name = "西门牛牛"
    test_question = "吃晚饭了吗？"
    request_data = {
        "user_name": test_user_name,
        "npc_name": test_npc_name,
        "question": test_question,
    }
    
    # 对 /chat/ 发起POST请求
    response = client.post("/chat/",json=request_data)
    
    # 检查响应是否为200 OK
    assert response.status_code == 200
    
    # 检查响应数据
    data = response.json()
    print(data)

# 调用测试函数
test_chat()