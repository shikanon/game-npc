# 引入所需模块
from fastapi.testclient import TestClient
import pytest
from gamenpc.webserver import app, npc_manager, user_manager
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.user import UserManager
from gamenpc.utils.config import Config

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