# coding:utf-8
"""
npc module.
author: shikanon
create: 2024/1/21
"""
import jinja2
import json, uuid
from typing import Dict, List
from datetime import datetime
from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import BaseMessage
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# from gamenpc import memory
from gamenpc.memory.memory import Mind, DialogueMemory, DialogueEntry
from gamenpc.model import doubao
from gamenpc.emotion import AffinityManager, AffinityLevel
from gamenpc.store.mysql import MySQLDatabase, Base
from gamenpc.store.redis import RedisList

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from dataclasses import dataclass


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



class NPC(Base):
    '''
    NPC名称、角色prompt模板、好感系统、场景
    '''
    def __init__(self, 
                 id=None,
                 name=None,
                 npc_id=None, 
                 user_id=None,   
                 score=None,  
                 scene=None, 
                 trait=None, 
                 affinity_level=None, 
                 dialogue_context=None,
                 affinity=AffinityManager, 
                 role_template_filename=None,
                 dialogue_summarize_num=20,
                 dialogue_round=6,
                 )->None:
        self.id = id
        self.name = name
        self.npc_id = npc_id
        self.user_id = user_id
        self.score = score
        self.scene = scene
        self.trait = trait
        self.affinity = affinity
        self.affinity_level = affinity_level
        self.event = None
        self.dialogue_round = dialogue_round
        #加载角色模板
        if role_template_filename == None:
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
        self.thoughts = Mind(model=model, character=trait)
        self.dialogue_manager = DialogueMemory(dialogue_context=dialogue_context, mind=self.thoughts, summarize_limit=dialogue_summarize_num)
        # character model
        self.character_model = doubao.ChatSkylark(
            model="skylark2-pro-character-4k",
            top_k=1,
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'npc_id': self.npc_id,
            'user_id': self.user_id,
            'score': self.score,
            'scene': self.scene,
            'trait': self.trait,
            'affinity_level': self.affinity_level,
            'dialogue_context': self.dialogue_context,
            'affinity': str(self.affinity),
            'role_template_filename': self.role_template_filename,
            'dialogue_summarize_num': self.dialogue_summarize_num,
            'dialogue_round': self.dialogue_round,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def get_character_info(self):
         return {
            'id': self.id,
            'name': self.name,
            'npc_id': self.npc_id,
            'user_id': self.user_id,
            'score': self.score,
            'scene': self.scene,
            'trait': self.trait,
            'affinity_level': self.affinity_level,
            'dialogue_context': self.dialogue_context,
            'affinity': str(self.affinity),
            'role_template_filename': self.role_template_filename,
            'dialogue_summarize_num': self.dialogue_summarize_num,
            'dialogue_round': self.dialogue_round,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def validate_template(self, text):
        for key in ["name","scene","affinity","trait","event"]:
            if key not in text:
                return False
        return True
    
    def set_character_model(self, model:BaseChatModel):
        '''变更人物对话模型'''
        self.character_model = model
    
    def set_scene(self, client: MySQLDatabase, scene:str):
        '''变更场景'''
        self.scene = scene
        update_data = {"scene": scene}
        condition = f"id='{self.id}'"
        client.update_record("npcs", update_data, condition)
    
    def get_scene(self):
        return self.scene
    
    def re_init(self, client: MySQLDatabase)->None:
        self.affinity.set_score(0)
        self.event = None
        self.dialogue_manager.clear(client)

    def set_dialogue_context(self, dialogue_context: List)->List:
        return self.dialogue_manager.set_contexts(dialogue_context)

    def get_dialogue_context(self)->List:
        return self.dialogue_manager.get_all_contexts()
    
    async def update_affinity(self, client: MySQLDatabase, player_name:str, content:str)->int:
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
            dialogue_content=content,
        )
        score = self.affinity.get_score()
        self.score = score
        client.update_record(NPCUser, self)
        return score

    
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

    async def chat(self, client: RedisList, player_name:str, content:str, content_type: str)->str:
        '''NPC对话'''
        self.system_prompt = self.render_role_template()
        all_messages = [
            SystemMessage(content=self.system_prompt)
        ]
        history_dialogues = self.dialogue_manager.get_recent_dialogue(round=self.dialogue_round)
        for dialog in history_dialogues:
            if dialog.role_from == self.name:
                all_messages.append(
                    AIMessage(content=dialog.content)
                )
            else:
                all_messages.append(
                    HumanMessage(content=dialog.content)
                )
        # 本次消息
        format_message = self.process_message(content)
        all_messages.append(HumanMessage(content=format_message))
        print(all_messages)

        if content_type == '':
            content_type = 'text'
        self.dialogue_manager.add_dialogue(redis_client=client, role_from=player_name, role_to=self.name, content=content, content_type=content_type)
    
        response = self.character_model(messages=all_messages)
        content = response.content
        self.dialogue_manager.add_dialogue(redis_client=client, role_from=self.name, role_to=player_name, content=content, content_type=content_type)

        return content



class NPCManager:
    def __init__(self, mysql_client: MySQLDatabase, redis_client: RedisList):
        self.client = mysql_client
        self.redis_client = redis_client

    def get_npcs(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[NPC]:
        npcs = self.client.select_records(record_class=NPC, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        # npc = self._instance_configs.get(npc_id)
        return npcs
    
    def get_npc(self, npc_id) -> List[NPC]:
        filter_dict = {'id': npc_id}
        npcs = self.client.select_record(record_class=NPC, filter_dict=filter_dict)
        # npc = self._instance_configs.get(npc_id)
        return npcs
    
    def set_npc(self, name: str, trait: str, short_description: str,
                               prompt_description: str, profile: str, chat_background: str, affinity_level_description: str)->NPC:
        new_npc= NPC(name=name, trait=trait, short_description=short_description,
                               prompt_description=prompt_description, profile=profile, chat_background=chat_background, affinity_level_description=affinity_level_description)
        new_npc = self.client.insert_record(new_npc)
        # self._instance_configs[new_npc.id] = new_npc
        return new_npc
    
    def get_npc_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[NPCUser]:
        npc_users = self.client.select_records(record_class=NPCUser, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        for npc_user in npc_users:
            # db中加载历史对话
            dialogue_context = self.redis_client.get_all("dialogue")
            npc_user.set_dialogue_context(dialogue_context)
        return npc_users

    
    def create_npc_user(self, name:str, user_id:str, npc_id:str, trait:str, scene: str) -> NPCUser:
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
            friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        affinity = AffinityManager(score=0,level=affinity_level)
        dialogue_context = []
        new_npc_user = NPCUser(name=name, user_id=user_id, npc_id=npc_id, trait=trait, scene=scene, affinity=affinity, dialogue_context=dialogue_context)
        new_npc_user = self.client.insert_record(new_npc_user)
        # self._instances[new_npc.id] = new_npc
        return new_npc_user