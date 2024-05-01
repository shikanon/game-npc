# coding:utf-8
import pytest
import asyncio
import re
from gamenpc.memory import memory
from gamenpc.model import doubao

model = doubao.ChatSkylark(
    model="skylark2-pro-4k",
    model_version="1.100",
    model_endpoint="mse-20231227193502-58xhk",
    top_k=1,
    )

@pytest.mark.asyncio
async def test_summarize_dialogue():
    prompt = "你是一名叫AI的程序员，Human是你朋友。"
    mem = memory.Mind(model,character=prompt)
    dialogues = [
        memory.DialogueEntry(role_from="Human", content="你好"),
        memory.DialogueEntry(role_from="AI", content="你好啊。今天过得怎么样？"),
        memory.DialogueEntry(role_from="Human", content="不怎么好，有点累了，想趴下~"),
        memory.DialogueEntry(role_from="AI", content="怎么了？是工作太辛苦了吗？"),
        memory.DialogueEntry(role_from="Human", content="不是，是心累，我感觉到中年危机"),
        memory.DialogueEntry(role_from="AI", content="你还年轻啊，怎么会有中年危机，是不是发生什么事了？"),
        memory.DialogueEntry(role_from="Human", content="我感觉身体一天不如一天了，提前买入中年，最近跑10公里累得够呛的"),
        memory.DialogueEntry(role_from="AI", content="啊？10 公里？！你是不是运动过度了，要注意身体啊，不要太拼命了。"),
    ]
    result = await mem.summarize_dialogue2converation(dialogues)
    print(result)

@pytest.mark.asyncio
async def test_DialogueMemory():
    prompt = "你是一名叫AI的程序员，Human是你朋友。"
    mind = memory.Mind(model,character=prompt)
    mem = memory.DialogueMemory(dialogue_context=[],mind=mind,summarize_limit=6)
    mem.add_dialogue(role_from="Human", content="你好")
    mem.add_dialogue(role_from="AI", content="你好啊。今天过得怎么样？")
    await asyncio.sleep(0.5)
    print(mem.get_recent_conversation())
    mem.add_dialogue(role_from="Human", content="不怎么好，有点累了，想趴下~")
    mem.add_dialogue(role_from="AI", content="怎么了？是工作太辛苦了吗？")
    await asyncio.sleep(0.5)
    print(mem.get_recent_conversation())
    mem.add_dialogue(role_from="Human", content="不是，是心累，我感觉到中年危机")
    mem.add_dialogue(role_from="AI", content="你还年轻啊，怎么会有中年危机，是不是发生什么事了？")
    await asyncio.sleep(0.5)
    print(mem.get_recent_conversation())
    mem.add_dialogue(role_from="Human", content="我感觉身体一天不如一天了，提前买入中年，最近跑10公里累得够呛的")
    mem.add_dialogue(role_from="AI", content="啊？10 公里？！你是不是运动过度了，要注意身体啊，不要太拼命了。")
    await asyncio.sleep(5)
    for c in mem.get_recent_conversation():
        print(c)

@pytest.mark.asyncio
async def test_all():
    character_prompt = "你是高远花梨，广播部高三学生，有着高雅的声音，容易害羞。"
    dialogues = []
    with open("./gamenpc/example/npc_scene.txt","r",encoding="utf-8") as fr:
        for line in fr.read().split("\n"):
            if line != "":
                dialogues.append(line)
    mind = memory.Mind(model=model,character=character_prompt)
    mem = memory.DialogueMemory(dialogue_context=[],mind=mind,summarize_limit=20)
    for content in dialogues:
        role_name = re.search(r'^(.*?)（', content).group(1)
        action = re.search(r'（(.*?)）', content).group(1)
        dialog = re.search(r'：(.*)', content).group(1)
        mem.add_dialogue(role=role_name, content=dialog)
        await asyncio.sleep(0.5)
    print(len(mem.get_all_conversation()))
    await asyncio.sleep(10)
    print(len(mem.get_all_conversation()))
    for c in mem.get_all_conversation():
        print(c)
        print(c.get_context())

@pytest.mark.asyncio
async def test_summarize_converation2event():
    prompt = "你是一名叫AI的程序员，Human是你朋友。"
    mem = memory.Mind(model,character=prompt)
    dialogues = [
        memory.ConverationEntry(
            scene="在广播部的活动中，市村龙之介称赞我的声音独特而动人",
            emotion="欢喜",
            emotion_reason="听到市村龙之介的称赞，我感到很开心。"
            ),
    ]
    result = await mem.summarize_converation2event(dialogues)
    print(result)