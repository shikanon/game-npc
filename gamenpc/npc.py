# coding:utf-8
"""
npc module.
author: shikanon
create: 2024/1/21
"""
import jinja2
import json
from typing import Dict, List
from datetime import datetime
from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import BaseMessage
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from gamenpc.memory import memory
from gamenpc.model import doubao
from gamenpc.emotion import AffinityManager, AffinityLevel


DEFAULT_ROLE_TEMPLATE = '''你的名字叫{{name}}。
{{scene}}
{{trait}}
{{affinity}}

# 对话规则

* 与游戏无关的请勿回答；
* 不要谈及政治和宗教话题；
* 不能暴露自己是AI或扮演游戏；
* 回答使用简体中文；回复尽量简洁；
* 回答内容不要使用双引号；
* 适当地引出新的话题；

{{event}}
'''


class NPC:
    '''
    NPC名称、角色prompt模板、好感系统、场景
    '''
    def __init__(self, 
                 name:str, 
                 trait:str, 
                 affinity:AffinityManager, 
                 scene='',
                 role_template_filename='',
                 dialogue_summarize_num=20,
                 dialogue_round=6,
                 )->None:
        self.name = name
        self.trait = trait
        self.scene = scene
        self.affinity = affinity
        self.event = None
        self.dialogue_round = dialogue_round
        #加载角色模板
        if role_template_filename == '':
            file_content = DEFAULT_ROLE_TEMPLATE
        else:
            with open(role_template_filename, 'r', encoding="utf-8") as fr:
                file_content = fr.read()
        if not self.validate_template(file_content):
            raise ValueError(f"模板错误，缺少必须的关键字")
        self.role_chat_template = jinja2.Template(file_content)
        # 记忆及思维
        model = doubao.ChatSkylark(
            model="skylark2-pro-32k",
            top_k=1,
        )
        self.thoughts = memory.Mind(model=model, character=trait)
        self.dialogue_manager = memory.DialogueMemory(mind=self.thoughts, summarize_limit=dialogue_summarize_num)
        # character model
        self.character_model = doubao.ChatSkylark(
            model="skylark2-pro-character-4k",
            top_k=1,
        )

    def get_character_info(self):
        return {
            "npc_name": self.name,
            "npc_trait": self.trait,
            "scene": self.scene,
            "event": self.event,
        }
    
    def validate_template(self, text):
        for key in ["name","scene","affinity","trait","event"]:
            if key not in text:
                return False
        return True
    
    def set_character_model(self, model:BaseChatModel):
        '''变更人物对话模型'''
        self.character_model = model
    
    def set_scene(self, scene:str):
        '''变更场景'''
        self.scene = scene
    
    def get_scene(self):
        return self.scene
    
    def re_init(self)->None:
        self.affinity.set_score(0)
        self.event = None
        self.dialogue_manager.clear()
    
    async def update_affinity(self, player_name:str, message:str)->int:
        '''更新好感度'''
        history = self.dialogue_manager.get_recent_dialogue(round=2)
        if history:
            history_dialogues = "\n".join(m.content for m in history)
        else:
            history_dialogues = ""
        self.affinity.calculate_affinity(
            npc=self.name, 
            target=player_name,
            history_dialogues=history_dialogues,
            dialogue_content=message,
        )
        return self.affinity.get_score()

    
    def render_role_template(self):
        '''渲染角色模板'''  
        if self.event:
            event = self.event.content
        else:
            event = ''
        return self.role_chat_template.render(
                name=self.name,
                scene=self.scene,
                trait=self.trait,
                event=event,
                affinity=str(self.affinity),
                )
    
    def process_message(self, message:str)->str:
        '''处理对话，加入外部变量'''
        return "当前时间：%s。\n%s"%(datetime.now().strftime("%A %B-%d %X"),message)
    
    async def thinking(self):
        '''NPC思考问题'''
        self.event = self.dialogue_manager.gen_topic_event()
        return self.event
    
    def get_thought_context(self)->str:
        '''获取NPC最近对话的思考'''
        conversations = self.dialogue_manager.get_recent_conversation()
        if conversations:
            return "\n".join(str(c) for c in conversations)
        else:
            return ""

    async def chat(self, player_name:str, message:str)->str:
        '''NPC对话'''
        self.system_prompt = self.render_role_template()
        all_messages = [
            SystemMessage(content=self.system_prompt)
        ]
        history_dialogues = self.dialogue_manager.get_recent_dialogue(round=self.dialogue_round)
        for dialog in history_dialogues:
            if dialog.role == self.name:
                all_messages.append(
                    AIMessage(content=dialog.content)
                )
            else:
                all_messages.append(
                    HumanMessage(content=dialog.content)
                )
        # 本次消息
        format_message = self.process_message(message)
        all_messages.append(HumanMessage(content=format_message))
        print(all_messages)
        response = self.character_model(messages=all_messages)
        anwser = response.content
        self.dialogue_manager.add_dialogue(role=player_name, content=message)
        self.dialogue_manager.add_dialogue(role=self.name, content=anwser)
        return anwser



class NPCManager:
    def __init__(self):
        self._instances = {}

    def get_npc(self, npc_name: str) -> NPC:
        if npc_name not in self._instances:
            raise ValueError('NPC %s not Exist.'%npc_name)
        return self._instances[npc_name]
    
    def create_npc(self, npc_name:str, npc_traits:str):
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
            friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        affinity = AffinityManager(score=0,level=affinity_level)
        self._instances[npc_name] = NPC(name=npc_name, trait=npc_traits, affinity=affinity)