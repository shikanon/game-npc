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

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


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
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    short_description = Column(String(255))
    trait = Column(String(255))
    prompt_description = Column(String(255))
    profile = Column(String(255))
    chat_background = Column(String(255))
    affinity_level_description = Column(String(255))
    knowledge_id = Column(String(64))
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, name=None, short_description=None, trait=None, prompt_description=None, profile=None, chat_background=None, 
                 affinity_level_description=None, knowledge_id=None, updated_at=None):
        self.id = id
        self.name = name
        self.short_description = short_description
        self.trait = trait
        self.prompt_description = prompt_description
        self.profile = profile
        self.chat_background = chat_background
        self.affinity_level_description = affinity_level_description
        self.knowledge_id = knowledge_id
        self.updated_at = updated_at

class NPCUser(Base):
        # 表的名字
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=str(uuid.uuid4()), unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # npc配置对象，外键
    # 通过关系关联NPCConfig对象
    npc = relationship('NPC')
    user_id = Column(String(255), ForeignKey('user.id'))  # 用户对象，外键
    # 通过关系关联User对象
    user = relationship('User')
    scene = Column(String(255))  # 场景描述
    score = Column(Integer)  # 好感分数
    affinity_level = Column(Integer)  # 亲密度等级
    created_at = Column(DateTime, default=datetime.now())  # 创建时间
    '''
    NPC名称、角色prompt模板、好感系统、场景
    '''
    def __init__(self, 
                 id=None,
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
        self.npc_id = npc_id
        self.user_id = user_id
        self.score = score
        self.scene = scene
        self.affinity = affinity
        self.affinity_level = affinity_level
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
        self.thoughts = Mind(model=model, character=trait)
        self.dialogue_manager = DialogueMemory(dialogue_context=dialogue_context, mind=self.thoughts, summarize_limit=dialogue_summarize_num)
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
    
    async def update_affinity(self, client: MySQLDatabase, player_name:str, message:str)->int:
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
        score = self.affinity.get_score()
        update_data = {"score": score}
        condition = f"id='{self.id}'"
        client.update_record("npcs", update_data, condition)
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

    async def chat(self, redis_client: RedisList, player_name:str, message:str, contentType: str)->str:
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
        format_message = self.process_message(message)
        all_messages.append(HumanMessage(content=format_message))
        print(all_messages)

        if contentType == '':
            contentType = 'text'
        self.dialogue_manager.add_dialogue(client=redis_client, role_from=player_name, role_to=self.name, content=message, contentType=contentType)
    
        response = self.character_model(messages=all_messages)
        anwser = response.content
        self.dialogue_manager.add_dialogue(client=redis_client, role_from=self.name, role_to=player_name, content=anwser, contentType=contentType)

        return anwser

class Scene(Base):
    __tablename__ = 'scene'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=str(uuid.uuid4()), unique=True)
    scene = Column(String(255))
    theater = Column(String(255))
    theater_event = Column(String(255))
    roles = Column(String(255))
    score = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, scene=None,  theater=None, theater_event=None, roles=None, score=None):
        self.id = id
        self.scene = scene
        self.theater = theater
        self.theater_event = theater_event
        self.roles = roles
        self.score = score


class NPCManager:
    def __init__(self, mysql_client: MySQLDatabase, redis_client: RedisList):
        self.client = mysql_client
        self.redis_client = redis_client
        # # 加载npc_user到内存中
        # self._instances = {}
        # npc_users = self.client.select_records(record_class=NPCUser)
        # for npc_user in npc_users:
        #     # 计算好感度
        #     affinity_level = AffinityLevel(
        #         acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
        #         familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
        #         friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
        #         soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
        #         adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        #     )
        #     affinity = AffinityManager(score=npc_user.score,level=affinity_level)
        #     npc_user.affinity = affinity

        #     # db中加载历史对话
        #     dialogue_context = []
        #     dialogue_records = self.client.select_records(record_class=DialogueEntry)
        #     for dialogue_record in dialogue_records:
        #         dialogue_id = dialogue_record[0]
        #         dialogue_role_from = dialogue_record[1]
        #         dialogue_role_to = dialogue_record[2]
        #         dialogue_content = dialogue_record[3]
        #         dialogue_context.append(DialogueEntry(dialogue_id, dialogue_role_from, dialogue_role_to, dialogue_content))
        #     npc_user.dialogue_context = dialogue_context

        #     self._instances[npc_user.id] = npc_user
        # print('self._instances: ', self._instances)

        # # 加载npc配置到内存中
        # self._instance_configs = {}
        # npcs = self.client.select_records(record_class=NPC)
        # for npc in npcs:
        #     self._instance_configs[npc.id] = npc
        # print('self._instance_configs: ', self._instance_configs)

    def get_npcs(self, order_by=None, filter_dict=None, page=1, per_page=10) -> List[NPC]:
        npcs = self.client.select_records(record_class=NPC, order_by=order_by, filter_dict=filter_dict, page=page, per_page=per_page)
        # npc = self._instance_configs.get(npc_id)
        return npcs
    
    def set_npc(self, npc_name: str, npc_traits: str)->NPC:
        new_npc= NPC(name=npc_name, trait=npc_traits)
        new_npc = self.client.insert_record(new_npc)
        # self._instance_configs[new_npc.id] = new_npc
        return new_npc
    
    def get_npc_users(self, order_by=None, filter_dict=None, page=1, per_page=10) -> List[NPCUser]:
        npc_users = self.client.select_records(record_class=NPCUser, order_by=order_by, filter_dict=filter_dict, page=page, per_page=per_page)
        for npc_user in npc_users:
            # db中加载历史对话
            dialogue_context = self.redis_client.get_all("dialogue")
            npc_user.set_dialogue_context(dialogue_context)
        return npc_users

    
    def create_npc(self, user_name:str, npc_name:str, npc_traits:str, scene: str) -> NPC:
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
            friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        affinity = AffinityManager(score=0,level=affinity_level)
        dialogue_context = []
        new_npc = NPC(name=npc_name, user_name=user_name, trait=npc_traits, scene=scene, affinity=affinity, dialogue_context=dialogue_context)
        new_npc = self.client.insert_record(new_npc)
        # self._instances[new_npc.id] = new_npc
        return new_npc