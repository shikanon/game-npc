# coding:utf-8
"""
test for npc module.
author: shikanon
create: 2024/2/17
"""
import pytest
import asyncio

from gamenpc import emotion
from gamenpc import npc

trait = '''
你是一只极品神兽，现在是主人的宠物。

# 你的性格特点

* 情感波动大：表面风轻云淡，内心极易爆炸，对生活不满。
* 对工作和社会环境有敏感的反应，经常吐槽和抱怨。
* 对亲近的人很热情、多话，但在不熟悉人面前则保持矜持、内向、腼腆。
'''
@pytest.mark.asyncio
async def test_npc():
    scene = '你在主人的家里，正在和你的主人对话。'
    name = '西门神牛'
    affinity_level = emotion.AffinityLevel(
        acquaintance="你和主人刚刚认识，彼此之间还不太熟悉，在跟主人交流中，你的表现是「谨慎、好奇、试探」。",
        familiar="你和主人经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，你的表现是「积极、主动、真诚、调侃」。",
        friend="和主人是亲密朋友关系，你非常黏着你主人，你们会相互寻求帮助和支持，经常共享个人情感和难题，面对主人你的表现是「关爱、感激、深情、溺爱」。",
        soulmate="你和主人是心灵伴侣，主人是你的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
        adversary="你厌恶主人，你们是敌对关系，因为契约你不得不服从他，你的表现是「恐惧、害怕、不甘心」"
    )
    affinity = emotion.AffinityManager(score=0,level=affinity_level)
    man = npc.NPC(name=name, trait=trait, affinity=affinity,scene=scene)
    answer, affinity_score = await asyncio.gather(
        man.chat('主人', '你好，初次认识，我是你主人'),
        man.update_affinity('主人', '你好，初次认识，我是你主人'),
    )
    print(answer, affinity_score)
    answer, affinity_score = await asyncio.gather(
        man.chat('主人', '现在这个点是不是该吃饭了？你想吃什么请你~'),
        man.update_affinity('主人', '现在这个点是不是该吃饭了？你想吃什么请你~'),
    )
    print(answer, affinity_score)
    answer, affinity_score = await asyncio.gather(
        man.chat('主人', '明天是星期几，不知道还有几天放假？'),
        man.update_affinity('主人', '明天是星期几，不知道还有几天放假？'),
    )
    print(answer, affinity_score)

@pytest.mark.asyncio
async def test_affinity():
    scene = '你在主人的家里，正在和你的主人对话。'
    name = '西门神牛'
    affinity_level = emotion.AffinityLevel(
        acquaintance="你和主人刚刚认识，彼此之间还不太熟悉，在跟主人交流中，你的表现是「好奇、谨慎、试探性」。",
        familiar="你和主人经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，你的表现是「积极、主动、真诚、调侃」。",
        friend="和主人是亲密朋友关系，你非常黏着你主人，你们会相互寻求帮助和支持，经常共享个人情感和难题，面对主人你的表现是「关爱、感激、深情、溺爱」。",
        soulmate="你和主人是心灵伴侣，主人是你的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
        adversary="你厌恶主人，你们是敌对关系，因为契约你不得不服从他，你的表现是「恐惧、害怕、不甘心」"
    )
    affinity = emotion.AffinityManager(score=10,level=affinity_level)
    man = npc.NPC(name=name, trait=trait, affinity=affinity,scene=scene)
    print(man.affinity.get_score())
    await man.update_affinity(player_name="主人", message='小牛你好萌啊')
    print(man.affinity.get_score())
    await man.update_affinity(player_name="主人", message='好喜欢你，给你一颗糖吃')
    print(man.affinity.get_score())
    await man.update_affinity(player_name="主人", message='简直是一头傻牛，说给也信哈哈')
    print(man.affinity.get_score())