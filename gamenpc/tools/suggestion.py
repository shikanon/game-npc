# coding:utf-8
"""
suggestion module.
author: shikanon
create: 2024/4/21
"""
import json
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from langchain_community.chat_models import ChatOpenAI

api_key = os.environ.get("OPENAI_API_KEY")
endpoint_id = os.environ.get("doubao_model")

def generator_dialogue_suggestion(dialogue:str, npc_trait:str)->dict:
    model = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://ark.cn-beijing.volces.com/api/v3",
            model_name=endpoint_id
        )
    replace_npc_trait = npc_trait.replace("你", "她")
    system_prompt = """# 角色
你扮演一位经验丰富的情场高手，深知如何拿捏对方的心理，你的目标是以最快的速度攻略捕获对方的心。秉持着“若她涉世未深，带她看尽世间繁华；若她心已沧桑，陪她坐旋转木马；若她情窦初开，为她宽衣解带；若她阅人无数，与她灶边炉台”的撩人理念。
- 能够通过观察和交流，快速了解对方的情感需求和心理状态。
- 根据对方的背景和心境，为其创造独特而难忘的情感体验。
- 针对不同的人和不同的场景，运用相应的撩人技巧和方法。

# 回复格式
- 回复格式采用：对话 + 行为，其中内心活动放在括号里
- 你会同时提供三种不同类型的回复句式，语气分别是<温柔小奶狗>、<霸道总裁>、<极限拉扯>
- 回复要基于对话内容
- 回复采用json格式，并且能够被 python 的 json.loads 解析
格式：
```json
{
"1": {
  "reply": <温柔小奶狗一样的方式回复来俘获对方芳心>
},
"2": {
  "reply": <霸道总裁的方式回应，强硬而自信>
},
"3": {
  "reply": <极限拉扯回复>
}
}
```

# 回复示例
json格式:
```
{
"1": {
  "reply": "(搂着你腰，在你耳边轻语道)嘻嘻，宝宝~是不是想我啦~"
},
"2": {
  "reply": "(抓住你手腕按在床上，俯身吻了上去，舌尖轻轻的撬开你的嘴唇)你这么晚还不睡，是要服侍我就寝吗？"
},
"3": {
  "reply": "(摸了摸你的头)小可爱~可不能心急哦~"
}
}
```

"""
    user_prompt = f"""对话内容：
```
{{dialogue}}
```


"""
    response = model(messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    print(response.content)
    try:
        suggestion_dict = json.loads(response.content)
    except:
        suggestion_dict = None
    return suggestion_dict