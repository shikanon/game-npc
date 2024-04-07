# 引入所需模块
from fastapi.testclient import TestClient
import pytest
from gamenpc.webserver import app, npc_manager, user_manager
from io import BytesIO
import json

# users = user_manager.get_users()
# user = users[0]
# npcs = npc_manager.get_npcs()
# npc = npcs[0]

# user_id = user.id
# npc_id = npc.id

# 创建测试客户端
client = TestClient(app)

@pytest.mark.asyncio
async def test_debug_chat():
    # 创建mock ChatRequest对象
    users = user_manager.get_users()
    user = users[0]
    npcs = npc_manager.get_npcs()
    npc = npcs[0]
    mock_request = {
        'user_id': str(user.id),
        'npc_id': str(npc.id),
        'question': '你好呀',
        'scene': '在家中',
        'content_type': 'text'
    }
    # 发起网络请求
    response = await client.post('/npc/debug_chat', json=mock_request)
    # 验证响应状态是否为200
    assert response.status_code == 200
    
    # 提取响应数据
    result = response.json()
    
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'message' in result
    assert result['message'] == '返回成功'
    assert 'debug_message' in result['data']
    assert 'total_time' in result['data']
    assert type(result['data']['total_time']) is float


# @pytest.mark.asyncio
# async def test_get_npc_users():
#     # 创建mock request对象
#     payload = {
#         "user_id": user_id,
#         "npc_id": npc_id,
#         "order_by": {"id": False},
#         "page": 1,
#         "limit": 10   
#     }
#     # 发起网络请求
#     response = await client.post("/npc/get_npc_users", json=payload)
#     # 验证响应状态是否为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result


# @pytest.mark.asyncio
# async def test_get_npc_all_info():
#     # 创建mock request对象
#     payload = {
#         "user_id": user_id,
#         "npc_id": npc_id,
#     }
#     # 发起网络请求
#     response = await client.post("/npc/get_npc_all_info", json=payload)
#     # 验证响应状态是否为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result


# @pytest.mark.asyncio
# async def test_get_history_dialogue():
#     # 创建Mock request对象
#     payload = {
#         "user_id": user_id,
#         "npc_id": npc_id,
#     }
#     # 发出网络请求
#     response = await client.post("/npc/get_history_dialogue", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result


# @pytest.mark.asyncio
# async def test_clear_history_dialogue():
#     # 创建 mock request 对象
#     payload = {
#         "user_id": user_id,
#         "npc_id": npc_id,
#     }
#     # 发起网络请求
#     response = await client.post("/npc/clear_history_dialogue", json=payload)
#     # 验证响应状态是否为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证返回结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '记忆、好感重置成功!'
#     assert 'data' in result   


# @pytest.mark.asyncio
# async def test_create_npc():
#     # 建立mock request对象
#     payload = {
#         "name": "NPC_1",
#         "trait": "Brave",
#         "sex": 1,
#         "short_description": "A brave NPC",
#         "prompt_description": "Be brave",
#         "profile": "xxx",
#         "chat_background": "xxx",
#         "affinity_level_description": "xxx"
#     }
#     # 发起网络请求
#     response = await client.post("/npc/create", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'


# @pytest.mark.asyncio
# async def test_update_npc():
#     # 创建 mock request 对象
#     payload = {
#         "id": npc_id,
#         "name": "NPC_2",
#         "trait": "Coward",
#         "short_description": "A coward NPC",
#         "prompt_description": "Be scared",
#         "profile": "",
#         "chat_background": "",
#         "affinity_level_description": ""
#     }
#     # 发出网络请求
#     response = await client.post("/npc/update", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result
#     assert result['data']['name'] == payload['name']
#     assert result['data']['trait'] == payload['trait']
#     assert result['data']['short_description'] == payload['short_description']
#     assert result['data']['prompt_description'] == payload['prompt_description']
#     assert result['data']['status'] == 0


# @pytest.mark.asyncio
# async def test_update_npc_status():
#     # 创建 mock request 对象
#     payload = {
#         "id": npc_id,
#         "status": 1
#     }
#     # 发起网络请求
#     response = await client.post("/npc/update_status", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证返回结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result
#     assert result['data']['status'] == payload['status']


# @pytest.mark.asyncio
# async def test_query_npc():
#     # 创建 mock request 对象
#     payload = {}
    
#     # 发起网络请求
#     response = await client.post("/npc/query", json=payload)
#     # 验证响应状态为200 
#     assert response.status_code == 200
#     # 提取响应数据
#     result = response.json()

#     # 验证返回结果
#     assert 'code' in result
#     assert result['code'] == 0
#     assert 'msg' in result
#     assert result['msg'] == '执行成功'
#     assert 'data' in result
#     assert 'list' in result['data']
#     assert 'total' in result['data']


# @pytest.mark.asyncio
# async def test_get_npc():
#     # mock request 对象
#     payload = {
#         "id": npc_id,
#     }
#     response = await client.post("/npc/get", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 提取响应的数据
#     result = response.json()
#     # 验证返回结果
#     assert result["code"] == 0
#     assert result['msg'] == '执行成功'
#     assert 'data' in result


# @pytest.mark.asyncio
# async def test_remove_npc():
#     # mock request 对象
#     payload = {
#         "id": npc_id,
#     }
#     # 发起网络请求
#     response = await client.post("/npc/remove", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 获取响应的 json 数据
#     result = response.json()
#     # 验证返回结果
#     assert 'code' in result
#     assert result['code'] == 0


# @pytest.mark.asyncio
# async def test_shift_scenes():
#     payload = {
#         "user_id": user_id,
#         "npc_id": npc_id,
#         "scene": "在办公室"
#     }

#     # 发起网络请求
#     response = await client.post("/npc/shift_scenes", json=payload)
#     # 验证响应状态为200
#     assert response.status_code == 200
#     # 获取响应的 json 数据
#     result = response.json()
#     # 验证返回结果
#     assert result['msg'] == '场景转移成功'


# @pytest.mark.asyncio
# async def test_user_register():
#     # 创建 mock 数据
#     payload = {
#             "name": "test_chen",
#             "sex": 1,
#             "phone": "12345678900",
#             "password": "test123"
#         }
    
#     # 访问 /user/register 接口
#     response = await client.post("/user/register", json=payload)
#     # 验证响应状态是否为 200
#     assert response.status_code == 200
#     # 提取响应数据
#     resp_data = response.json()
    
#     # 验证响应结果
#     assert 'code' in resp_data
#     assert resp_data['code'] == 0
#     assert 'msg' in resp_data
#     assert resp_data['msg'] == '执行成功'
    
#     assert 'data' in resp_data
#     assert resp_data['data']['name'] == payload['name']
#     assert resp_data['data']['sex'] == payload['sex']
#     assert resp_data['data']['phone'] == payload['phone']
#     assert resp_data['data']['password'] == payload['password']


# @pytest.mark.asyncio
# async def test_user_login():
#     # 创建 mock 数据
#     login_payload = {
#         "name": "test_chen",
#         "password": "test123"
#     }
#     # 调用用户登录接口
#     login_response = await client.post("/user/login", json=login_payload)
#     # 验证响应状态码为 200
#     assert login_response.status_code == 200
#     # 提取响应数据
#     resp_data = login_response.json()
    
#     # 验证响应结果
#     assert 'code' in resp_data
#     assert resp_data['code'] == 0
#     assert 'msg' in resp_data
#     assert resp_data['msg'] == '执行成功'
#     assert 'data' in resp_data
#     assert resp_data['data'] is not None


# @pytest.mark.asyncio
# async def test_query_user():
#     # 创建 mock 数据
#     payload = {
#         "id": user_id,
#     }
#     # 调用查询用户接口
#     response = await client.post("/user/query", json=payload)
#     # 验证响应状态码为 200
#     assert response.status_code == 200
#     # 提取响应数据
#     resp_data = response.json()
    
#     # 验证响应结果
#     assert 'code' in resp_data
#     assert resp_data['code'] == 0
#     assert 'msg' in resp_data
#     assert resp_data['msg'] == '执行成功'
#     assert 'data' in resp_data
#     assert resp_data['data'] is not None


# @pytest.mark.asyncio
# async def test_update_user():
#     # 创建 mock 数据
#     payload = {
#         "id": user_id,
#         "name": "new_test_user",
#         "sex": 2,
#         "phone": "09876543210",
#         "password": "new_12345"
#     }
#     # 调用更新用户接口
#     response = await client.post("/user/update", json=payload)
#     # 验证响应状态为 200
#     assert response.status_code == 200
#     # 提取响应数据
#     resp_data = response.json()
    
#     # 验证响应结果
#     assert 'code' in resp_data
#     assert resp_data['code'] == 0
#     assert 'msg' in resp_data
#     assert resp_data['msg'] == '执行成功'
#     assert 'data' in resp_data
#     assert resp_data['data']['name'] == payload['name']
#     assert resp_data['data']['sex'] == payload['sex']
#     assert resp_data['data']['phone'] == payload['phone']


# import pytest

# @pytest.mark.asyncio
# async def test_remove_user():
#     # 创建 mock 数据
#     payload = {
#         "id": user_id,
#     }
#     # 调用移除用户接口
#     response = await client.post("/user/remove", json=payload)
#     # 验证响应状态码为 200
#     assert response.status_code == 200
#     # 提取响应数据
#     resp_data = response.json()
    
#     # 验证响应结果
#     assert 'code' in resp_data
#     assert resp_data['code'] == 0
#     assert 'msg' in resp_data
#     assert resp_data['msg'] == '执行成功'


# @pytest.mark.asyncio
# async def test_upload_file():
#     # 创建 mock 数据
#     payload = {
#         'image_type': 1
#     }
#     testing_file = BytesIO(b"Testing contents")
#     # 调用文件上传接口
#     response = await client.post("/npc/file_upload", data=payload, files={"file": ("test.png", testing_file, "text/plain")})
#     # 验证响应状态码为 200
#     assert response.status_code == 200
#     # 提取响应数据
#     resp_data = json.loads(response.text)
#     print('resp_data: --------------------------', resp_data)
