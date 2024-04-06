# coding:utf-8
"""
npc module.
author: shikanon
create: 2024/4/4
"""
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from gamenpc.model import doubao

def generator_npc_trait(name:str, sex:str, short_description:str):
    model = doubao.ChatSkylark(
        model="skylark2-pro-4k",
    )
    system_prompt = """你是一位富有想象力且专业的AI提示词工程师，你擅长以独特的才思和想象力，打造出精致和符合用户需求的AI对话提示。
- 你可以准确地认识到用户给出的角色姓名、性别以及性格特征，根据这些信息塑造具特色的虚拟角色。
- 你将发挥你的创意和天马行空的想象力，为角色塑造丰富而鲜明的性格，并描述这一系列性格形成背后的成长经历和心理变化。
- 根据你对角色的理解和构思，通过细节来营造角色的性格特征，使整个角色栩栩如生、充满吸引力，比如他们的口头禅、特有的语气风格、对待爱情的态度、招牌式动作等。
- 为了让AI更好地理解这些提示，你需要以简洁明了的格式呈现它们，如用“-”区分各主题，并用你描述。
"""
    user_prompt = f"""角色姓名：{name}
    性别：{sex}
    角色描述：{short_description}"""
    response = model(messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return response.content