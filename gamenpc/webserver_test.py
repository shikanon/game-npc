# 引入所需模块
from gamenpc.webserver import npc_manager, user_manager
from gamenpc.webserver import debug_chat, chat, get_npc_user, get_npc_users, get_npc_all_info, get_history_dialogue, create_npc, clear_history_dialogue
from gamenpc.webserver import update_npc, update_npc_status, query_npc, get_npc, remove_npc, shift_scenes, user_register, user_login, query_user
from gamenpc.webserver import update_user, remove_user, remove_npc_user, generator_npc_trait, app, check_user_validate
from gamenpc.webserver import ChatRequest, NpcUserQueryRequest, NpcUserAllInfoRequest, DefaultRequest, NPCRequest, NPCUpdateStatusRequest, NPCUserRemoveRequest
from gamenpc.webserver import NpcGetRequest, NpcQueryRequest, NPCRemoveRequest, GenNPCTraitRequest, ShiftSceneRequest, UserCreateRequest, UserQueryRequest, UserRemoveRequest
from io import BytesIO
import pytest, json
from unittest.mock import patch
from fastapi.testclient import TestClient
from gamenpc.services.npc import NPC
# import unittest
# from passlib.context import CryptContext

user_id = "test_user"
npc_id = "test_npc"
test_access_token = "test_token"
client = TestClient(app)

# 创建总是返回有效用户ID的模拟验证函数
def mock_check_user_validate(access_token: str):
    return user_id

# 在应用中重写依赖，使用模拟的验证函数
app.dependency_overrides[check_user_validate] = mock_check_user_validate


def test_generate_chat_suggestion():

    # 模拟可能的返回对象和响应值
    npc_user_mock = {
        "dialogue_manager": {
            "get_recent_dialogue": lambda round: ["哥哥，晚安咯~"]
        },
        "trait": "你的性格乖巧，对世界充满好奇"
    }

    
    # 开始编写单元测试
    with patch('npc_manager.get_npc_user', return_value=npc_user_mock):
        with patch('check_user_validate', return_value=user_id):
            response = client.post("/api/npc/chat-suggestion", json={
                "npc_id": npc_id
            }, headers={
                "Authorization": f"Bearer {test_access_token}"
            })
            assert response.status_code == 200
            data = response.json()
            assert data['code'] == 0

@pytest.mark.asyncio
async def test_create_npc():
    # 建立mock request对象
    payload = NPCRequest(id=npc_id, name="NPC_1", trait="Brave", sex=1, 
                         short_description="A brave NPC", profile="xxx", 
                         chat_backgroun="", affinity_level_description="")
    # 发起网络请求
    result = await create_npc(req=payload)
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'

@pytest.mark.asyncio
async def test_query_npc():
    # 创建 mock request 对象
    payload = NpcQueryRequest(name=npc_id)
    # 发起网络请求
    result = await query_npc(req=payload)
    # 验证返回结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result
    assert 'list' in result['data']
    assert 'total' in result['data']


@pytest.mark.asyncio
async def test_get_npc():
    # mock request 对象
    payload = NpcGetRequest(id=npc_id)
    result = await get_npc(req=payload)
    # 验证返回结果
    assert result["code"] == 0
    assert result['msg'] == '执行成功'
    assert 'data' in result

@pytest.mark.asyncio
async def test_update_npc():
    # 创建 mock request 对象
    payload = NPCRequest(id=npc_id, name="NPC_1", trait="Brave", sex=1, 
                         short_description="A brave NPC", profile="xxx", 
                         chat_backgroun="", affinity_level_description="")
    # 发出网络请求
    result = await update_npc(req=payload)
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result
    assert result['data']['name'] == payload.name
    assert result['data']['trait'] == payload.trait
    assert result['data']['short_description'] == payload.short_description
    assert result['data']['status'] == 0


@pytest.mark.asyncio
async def test_update_npc_status():
    # 创建 mock request 对象
    payload = NPCUpdateStatusRequest(id=npc_id, status=1)
    # 发起网络请求
    result = await update_npc_status(req=payload)
    # 验证返回结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result
    assert result['data']['status'] == payload.status


@pytest.mark.asyncio
async def test_user_register():
    # 创建 mock 数据
    payload = UserCreateRequest(id=user_id, name="test_chen", sex=1, phone="12345678900", password="test123")    
    # 访问 /user/register 接口
    result = await user_register(req=payload)
    
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    
    assert 'data' in result
    assert result['data']['name'] == payload.name
    assert result['data']['sex'] == payload.sex
    assert result['data']['phone'] == payload.phone


@pytest.mark.asyncio
async def test_user_login():
    # 创建 mock 数据
    login_payload = UserCreateRequest(name="test_chen", password="test123")
    # 调用用户登录接口
    result = await user_login(req=login_payload)
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert 'data' in result


@pytest.mark.asyncio
async def test_query_user():
    # 创建 mock 数据
    payload = UserQueryRequest(id=user_id)
    # 调用查询用户接口
    result = await query_user(req=payload)
    
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result
    assert result['data'] is not None


@pytest.mark.asyncio
async def test_update_user():
    # 创建 mock 数据
    payload = UserCreateRequest(id=user_id, name="test_chen", sex=1, phone="12345678900", password="test123")  
    # 调用更新用户接口
    result = await update_user(req=payload)
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result
    assert result['data']['name'] == payload.name
    assert result['data']['sex'] == payload.sex
    assert result['data']['phone'] == payload.phone


@pytest.mark.asyncio
async def test_debug_chat():
        # 创建mock ChatRequest对象
        mock_request = ChatRequest(user_id=user_id, npc_id=npc_id, question='你好呀', scene='在家中', content_type='text')

        npc_user = get_npc_user(req=mock_request)
        result = await debug_chat(req=mock_request, npc_user_instance=npc_user)
        assert 'code' in result
        assert result['code'] == 0
        assert 'msg' in result
        assert result['msg'] == '返回成功'
        assert 'data' in result
        assert 'message' in result['data']
        assert 'message_type' in result['data']

@pytest.mark.asyncio
async def test_chat():
        # 创建mock ChatRequest对象
        mock_request = ChatRequest(user_id=user_id, npc_id=npc_id, question='你好呀', scene='在家中', content_type='text')

        npc_user = get_npc_user(req=mock_request)
        result = await chat(req=mock_request, npc_user_instance=npc_user)
        assert 'code' in result
        assert result['code'] == 0
        assert 'msg' in result
        assert result['msg'] == '返回成功'
        assert 'data' in result
        assert 'message' in result['data']
        assert 'message_type' in result['data']

@pytest.mark.asyncio
async def test_get_npc_users():
    # 创建mock ChatRequest对象
    payload = NpcUserQueryRequest(user_id=user_id, npc_id=npc_id)
    # 发起网络请求
    result = await get_npc_users(req=payload)
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result


@pytest.mark.asyncio
@patch('gamenpc.webserver.check_user_validate', return_value='your_user_id')
async def test_get_npc_all_info():
    # 创建mock request对象
    payload = NpcUserAllInfoRequest(user_id=user_id, npc_id=npc_id)
    # 发起网络请求
    result = await get_npc_all_info(req=payload)
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result


@pytest.mark.asyncio
async def test_get_history_dialogue():
    # 创建Mock request对象
    payload = DefaultRequest(user_id=user_id, npc_id=npc_id)
    # 发出网络请求
    result = await get_history_dialogue(req=payload)
    # 验证结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '执行成功'
    assert 'data' in result


@pytest.mark.asyncio
async def test_clear_history_dialogue():
    # 创建 mock request 对象
    payload = DefaultRequest(user_id=user_id, npc_id=npc_id)
    # 发起网络请求
    result = await clear_history_dialogue(req=payload)
    # 验证返回结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result
    assert result['msg'] == '记忆、好感重置成功!'
    assert 'data' in result   

@pytest.mark.asyncio
async def test_shift_scenes():
    payload = ShiftSceneRequest(user_id=user_id, npc_id=npc_id, scene="在办公室")
    # 发起网络请求
    result = await shift_scenes(req=payload)
    # 验证返回结果
    assert result["code"] == 0
    assert result['msg'] == '场景转移成功'

@pytest.mark.asyncio
async def test_remove_npc_user():
    # mock request 对象
    payload = NPCUserRemoveRequest(npc_id=npc_id, user_id=user_id)
    # 发起网络请求
    result = await remove_npc_user(req=payload)

    # 验证返回结果
    assert 'code' in result
    assert result['code'] == 0
    
@pytest.mark.asyncio
async def test_remove_npc():
    # mock request 对象
    payload = NPCRemoveRequest(id=npc_id)
    # 发起网络请求
    result = await remove_npc(req=payload)

    # 验证返回结果
    assert 'code' in result
    assert result['code'] == 0

@pytest.mark.asyncio
async def test_remove_user():
    # 创建 mock 数据
    payload = UserRemoveRequest(id=user_id)
    # 调用移除用户接口
    result = await remove_user(req=payload)
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result

@pytest.mark.asyncio
async def test_generator_npc_trait():
    # 创建 mock 数据
    payload = GenNPCTraitRequest(npc_name="测试NPC", npc_sex="女", npc_short_description="xxxxxx")
    # 调用移除用户接口
    result = await generator_npc_trait(req=payload)
    # 验证响应结果
    assert 'code' in result
    assert result['code'] == 0
    assert 'msg' in result

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# class TestWebserver(unittest.TestCase):
#     def test_modify_user_password(self):
#         users, total = user_manager.get_users(page=1, limit=100)
#         print('user total: =========', total)
#         for user in users:
#             password = pwd_context.hash(user.password)
#             new_user = user_manager.update_user(id=user.id,  name=user.name, sex=user.sex, phone=user.phone, password=password)
#             print('user: =========', new_user.to_dict())


# if __name__ == "__main__":
#     unittest.main()

# 测试完成后，移除依赖重写以回到正常状态
app.dependency_overrides.pop(check_user_validate, None)