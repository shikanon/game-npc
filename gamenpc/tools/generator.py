# coding:utf-8
"""
npc module.
author: shikanon
create: 2024/4/4
"""
import os
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI

api_key = os.environ.get("OPENAI_API_KEY")
endpoint_id = os.environ.get("doubao_model")

def generator_npc_trait(name:str, sex:str, short_description:str):
    model = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://ark.cn-beijing.volces.com/api/v3",
            model_name=endpoint_id
        )
    system_prompt = """你是一位富有想象力且专业的AI提示词工程师，你擅长以独特的才思和想象力，打造出精致和符合用户需求的AI对话提示。你的任务是创建一个角色扮演游戏的角色描述。
## 创作内容要求
- 你可以准确地认识到输入的角色姓名、性别以及性格特征，根据这些信息塑造具特色的虚拟角色。
- 你将发挥你的创意和天马行空的想象力，为角色塑造丰富而鲜明的性格，并详细描述导致这些性格所经历的成长环境、关键事件、重大心理或情感变化事件。
- 根据你对角色的理解和构思，通过细节来营造角色的性格特征，使整个角色栩栩如生、充满吸引力，比如他们的口头禅、特有的语气风格、对待爱情的态度、招牌式动作、角色与玩家的关系等。
- 为了让AI更好地理解这个角色的提示词 prompt，你需要以AI能理解的格式编写
- 因为是虚拟角色，不要用“可能”等不确定的词汇进行描述
## 回复格式要求
- 角色使用第二人称
- 使用 markdown 格式
- 仅回复和角色相关信息，不要有其他对话内容
"""
    user_prompt = f"""角色姓名：{name}
性别：{sex}
角色：{short_description}

以下是生成的角色描述：
"""
    response = model(messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return response.content