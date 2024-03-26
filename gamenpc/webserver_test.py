# test_main.py
from io import BytesIO
import json
import unittest
import requests

base_url = "http://127.0.0.1:8888/api"
client = requests.Session()
npc_id = ""
user_id = ""
name = "NPC_2"
class TestAPI(unittest.TestCase):
    # def test_chat(self):
    #     payload = {
    #         "user_id": user_id,
    #         "npc_id": npc_id,
    #         "scene": "battlefield",
    #         "question": "好了嘛，知道了，但是你不能这么对我啊",
    #         "content_type": "text",   
    #     }
    #     response = client.post(f"{base_url}/npc/chat", json=payload)
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '返回成功'
    #     assert 'data' in resp_data
    #     assert 'message' in resp_data['data']
    #     assert 'message_type' in resp_data['data']
    #     assert 'affinity_score' in resp_data['data']

    # def test_get_npc_users(self):
    #     payload = {
    #         # "user_id": user_id,
    #         # "npc_id": npc_id,
    #         # "order_by": {"id": False},
    #         # "page": 1,
    #         # "limit": 10   
    #     }
    #     response = client.post(f"{base_url}/npc/get_npc_users", json=payload)
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     print('response.status_code: --------------------------', response.status_code)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data

    # def test_get_npc_all_info(self):
    #     payload = {
    #         "user_id": user_id,
    #         "npc_id": npc_id,
    #     }
    #     response = client.post(f"{base_url}/npc/get_npc_all_info", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)c
    #     print('response.status_code: --------------------------', response.status_code)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data

    # def test_get_history_dialogue(self):
    #     payload = {
    #         "user_id": user_id,
    #         "npc_id": npc_id,
    #     }
    #     response = client.post(f"{base_url}/npc/get_history_dialogue", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data

    # def test_clear_history_dialogue(self):
    #     payload = {
    #         "user_id": user_id,
    #         "npc_id": npc_id,
    #     }
    #     response = client.post(f"{base_url}/npc/clear_history_dialogue", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '记忆、好感重置成功!'
    #     assert 'data' in resp_data

    # def test_create_npc(self):
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
    #     response = client.post(f"{base_url}/npc/create", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert resp_data['data']['name'] == payload['name']
    #     assert resp_data['data']['trait'] == payload['trait']
    #     assert resp_data['data']['sex'] == payload['sex']
    #     assert resp_data['data']['profile'] == payload['profile']
    #     assert resp_data['data']['chat_background'] == payload['chat_background']
    #     assert resp_data['data']['affinity_level_description'] == payload['affinity_level_description']
    #     assert resp_data['data']['short_description'] == payload['short_description']
    #     assert resp_data['data']['prompt_description'] == payload['prompt_description']

    #     npc_id = resp_data['data']['id']
    # def test_update_npc(self):
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
    #     response = client.post(f"{base_url}/npc/update", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert resp_data['data']['name'] == payload['name']
    #     assert resp_data['data']['trait'] == payload['trait']
    #     assert resp_data['data']['short_description'] == payload['short_description']
    #     assert resp_data['data']['prompt_description'] == payload['prompt_description']
    #     assert resp_data['data']['status'] == 0

    # def test_update_npc_status(self):
    #     payload = {
    #         "id": npc_id,
    #         "status": 1
    #     }
    #     response = client.post(f"{base_url}/npc/update_status", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert resp_data['data']['status'] == payload['status']

    # def test_query_npc(self):
    #     payload = {
    #         "name": name,
    #         "page": 1,
    #         "limit": 10
    #     }
    #     response = client.post(f"{base_url}/npc/query", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert 'list' in resp_data['data']
    #     assert 'total' in resp_data['data']

    # def test_get_npc(self):
    #     payload = {
    #         "id": npc_id,
    #     }
    #     response = client.post(f"{base_url}/npc/get", json=payload)
    #     assert response.status_code == 200                                  
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data

    # def test_remove_npc(self):
    #     payload = {
    #         "id": npc_id,
    #     }
    #     response = client.post(f"{base_url}/npc/remove", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 

    # def test_shift_scenes(self):
    #     payload = {
    #         "user_id": user_id,
    #         "npc_id": npc_id,
    #         "scene": "在办公室"
    #     }
    #     response = client.post(f"{base_url}/npc/shift_scenes", json=payload)
    #     assert response.status_code == 200
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert resp_data['msg'] == '场景转移成功'

    # def test_user_register_login(self):
    #     payload = {
    #         "name": "test_chen",
    #         "sex": 1,
    #         "phone": "12345678900",
    #         "password": "test123"
    #     }
    #     response = client.post(f"{base_url}/user/register", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert resp_data['code'] == 0
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert resp_data['data']['name'] == payload['name']
    #     assert resp_data['data']['sex'] == payload['sex']
    #     assert resp_data['data']['phone'] == payload['phone']
    #     assert resp_data['data']['password'] == payload['password']

    # # def test_user_login(self):
    #     login_payload = {
    #         "name": "test_chen",
    #         "password": "test123"
    #     }
    #     login_response = client.post(f"{base_url}/user/login", json=login_payload)
    #     assert login_response.status_code == 200 
    #     resp_data = login_response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert resp_data['code'] == 0
    #     assert resp_data['msg'] == '执行成功'
    #     assert resp_data['data'] is not None

    #     user_id = resp_data['data']['id']
    # # def test_query_user(self):
    #     payload = {
    #         "id": user_id,
    #     }
    #     response = client.post(f"{base_url}/user/query", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert resp_data['data'] is not None

    # def test_update_user(self):
    #     payload = {
    #         "id": user_id,
    #         "name": "new_test_user",
    #         "sex": 2,
    #         "phone": "09876543210",
    #         "password": "new_12345"
    #     }
    #     response = client.post(f"{base_url}/user/update", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'
    #     assert 'data' in resp_data
    #     assert resp_data['data']['name'] == payload['name']
    #     assert resp_data['data']['sex'] == payload['sex']
    #     assert resp_data['data']['phone'] == payload['phone']
    
    # def test_remove_user(self):
    #     payload = {
    #         "id": user_id,
    #     }
    #     response = client.post(f"{base_url}/user/remove", json=payload)
    #     assert response.status_code == 200 
    #     resp_data = response.json()
    #     print('resp_data: --------------------------', resp_data)
    #     assert 'code' in resp_data
    #     assert resp_data['code'] == 0 
    #     assert 'msg' in resp_data
    #     assert resp_data['msg'] == '执行成功'

    def test_upload_file(self):
        payload = {
            'image_type': 1
        }
        testing_file = BytesIO(b"Testing contents")
        response = client.post(f"{base_url}/npc/file_upload", data=payload, files={"file": ("test.txt", testing_file, "text/plain")})

        assert response.status_code == 200
        resp_data = json.loads(response.text)
        print('resp_data: --------------------------', resp_data)
        
if __name__ == '__main__':
    unittest.main()