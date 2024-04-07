# coding:utf-8
"""
npc module.
author: shikanon
create: 2024/1/21
"""
import jinja2
import json, uuid, pickle
from typing import Dict, List
from datetime import datetime
from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import BaseMessage
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from gamenpc.memory.memory import Mind, DialogueMemory
from gamenpc.model import doubao
from gamenpc.emotion import AffinityManager, AffinityLevel
from gamenpc.store.mysql_client import MySQLDatabase, Base
from gamenpc.store.redis_client import RedisList
from gamenpc.utils.logger import debuglog

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from dataclasses import dataclass

# debuglog = DebugLogger("npc")

DEFAULT_ROLE_TEMPLATE = '''# 角色设定
你的名字叫{{name}}。
{{trait}}
{{scene}}
{{affinity}}

# 对话规则

* 不要谈及政治和宗教话题；
* 不能暴露自己是AI或扮演游戏，要符合角色设定；
* 回答使用简体中文；
* 回答内容不要使用双引号；
* 适当地增加新话题来增加互动性，但不要频繁；

{{event}}
'''

@dataclass
class NPC(Base):
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(64))
    short_description = Column(String(255))
    trait = Column(Text)
    sex = Column(Integer)  # NPC性别
    prompt_description = Column(Text)
    profile = Column(Text)
    chat_background = Column(Text)
    affinity_level_description = Column(Text)
    status = Column(Integer)
    knowledge_id = Column(String(255))
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, name=None, short_description=None, trait=None, sex=None, prompt_description=None, profile=None, chat_background=None, 
                 affinity_level_description=None, knowledge_id=None, updated_at=None):
        self.id = id
        self.name = name
        self.short_description = short_description
        self.trait = trait
        self.sex = sex
        self.prompt_description = prompt_description
        self.profile = profile
        self.status = 0
        self.chat_background = chat_background
        self.affinity_level_description = affinity_level_description
        self.knowledge_id = knowledge_id
        self.updated_at = updated_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'short_description': self.short_description,
            'trait': self.trait,
            'sex': self.sex,
            'prompt_description': self.prompt_description,
            'profile': self.profile,
            'status': self.status,
            'chat_background': self.chat_background,
            'affinity_level_description': self.affinity_level_description,
            'knowledge_id': self.knowledge_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

@dataclass
class NPCUser(Base):
        # 表的名字
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # npc配置对象，外键
    # 通过关系关联NPCConfig对象
    npc = relationship('NPC')
    user_id = Column(String(255), ForeignKey('user.id'))  # 用户对象，外键
    # 通过关系关联User对象
    user = relationship('User')
    name = Column(String(255))  # NPC名称
    sex = Column(Integer)  # NPC性别
    scene = Column(String(255))  # 场景描述
    trait = Column(Text)  # 场景描述
    score = Column(Integer)  # 好感分数
    affinity_level = Column(Text)  # 亲密度等级
    created_at = Column(DateTime, default=datetime.now())  # 创建时间
    '''
    NPC名称、角色prompt模板、好感系统、场景
    '''
    def __init__(self, 
                 id=None,
                 name=None,
                 npc_id=None, 
                 user_id=None,   
                 score=0,  
                 scene=None, 
                 sex=0, 
                 trait=None, 
                 affinity_level="", 
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
        self.sex = sex
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
            model_version="1.1"
        )
        self.debug_info = {}
    
    def to_dict(self):
        dialogue_context = self.get_dialogue_context()
        dialogue_context_list = [dialogue.to_dict() for dialogue in dialogue_context]

        # short_description = npc.short_description
        # prompt_description = npc.prompt_description
        # profile = npc.profile
        # chat_background = npc.chat_background
        # affinity_level_description = npc.affinity_level_description
        return {
            'id': self.id,
            'name': self.name,
            'npc_id': self.npc_id,
            'user_id': self.user_id,
            'score': self.score,
            'sex': self.sex,
            'scene': self.scene,
            'trait': self.trait,
            # 'short_description': short_description,
            # 'prompt_description': prompt_description,
            # 'profile': profile,
            # 'chat_background': chat_background,
            # 'affinity_level_description': affinity_level_description,
            'dialogue_context': dialogue_context_list,
            'affinity_level': self.affinity_level,
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
            'sex': self.sex,
            'scene': self.scene,
            'trait': self.trait,
            'affinity_level': self.affinity_level,
            'dialogue_round': self.dialogue_round,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def init(self, 
             redis_client: RedisList, 
             role_template_filename=None,
             dialogue_summarize_num=20,
            dialogue_round=6):
        # db中加载历史对话
        dialogue_context = []
        list_name = f'dialogue_{self.npc_id}_{self.user_id}'
        dialogue_context_bytes_list = redis_client.get_all(list_name)

        for dialogue_context_byte in dialogue_context_bytes_list:
            # 这里将dialogue_context_byte转成dialogue
            dialogue = pickle.loads(dialogue_context_byte)
            dialogue_context.append(dialogue)
        dialogue_context.reverse()
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识不久，虽然互有好感，但彼此之间还不太熟悉，在他面前你的表现是「害羞、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，并相互暧昧，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、挑逗、调侃」。",
            friend="你们已经是亲密关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「主动、溺爱、渴望、撒娇」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间心有灵犀，和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        self.affinity = AffinityManager(score=self.score,level=affinity_level)
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
        self.thoughts = Mind(model=model, character=self.trait)
        self.dialogue_manager = DialogueMemory(dialogue_context=dialogue_context, mind=self.thoughts, summarize_limit=dialogue_summarize_num)
        # character model
        self.character_model = doubao.ChatSkylark(
            model="skylark2-pro-character-4k",
            top_k=1,
            model_version="1.1"
        )
        return
    
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
        filter_dict = {'id': f'{self.npc_id}_{self.user_id}'}
        npc_user = client.select_record(NPCUser, filter_dict)
        npc_user.scene = scene
        self.scene = scene
        client.update_record(npc_user)
    
    def get_scene(self):
        return self.scene
    
    def re_init(self, client: RedisList, mysql_client: MySQLDatabase,)->None:
        self.affinity.set_score(60)
        self.event = None
        self.dialogue_manager.clear(client, self.id)
        mysql_client.update_record(self)

    def set_dialogue_context(self, dialogue_context: List)->List:
        return self.dialogue_manager.set_contexts(dialogue_context)

    def get_dialogue_context(self)->List:
        return self.dialogue_manager.get_all_contexts()
    
    async def update_affinity(self, client: MySQLDatabase, player_id:str, content:str)->int:
        '''更新好感度'''
        history = self.dialogue_manager.get_recent_dialogue(round=2)
        if history:
            history_dialogues = "\n".join(m.content for m in history)
        else:
            history_dialogues = ""
        self.affinity.calculate_affinity(
            npc=self.id, 
            target=player_id,
            history_dialogues=history_dialogues,
            dialogue_content=content,
        )
        self.affinity_level = self.affinity.get_relation_level()
        self.score = self.affinity.get_score()
        client.update_record(self)
        return self.score

    
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
                affinity=self.affinity,
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

    async def chat(self, client: RedisList, player_id:str, content:str, content_type: str)->str:
        '''NPC对话'''
        self.system_prompt = self.render_role_template()
        all_messages = [
            SystemMessage(content=self.system_prompt)
        ]
        history_dialogues = self.dialogue_manager.get_recent_dialogue(round=self.dialogue_round)
        for dialog in history_dialogues:
            if dialog.role_from == self.id:
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
        debuglog.info(f'chat: all_messages === {all_messages}')

        if content_type == '':
            content_type = 'text'
        
        list_name = f'dialogue_{self.id}'
        if self.dialogue_manager.check_dialogue():
            client.pop(list_name)

        call_dialogue = self.dialogue_manager.add_dialogue(role_from=player_id, role_to=self.id, content=content, content_type=content_type)
        debuglog.info(f'chat: call_dialogue === {call_dialogue.to_dict()}')

        self.debug_info["模型输入"] = all_messages
        debuglog.info(f'chat输入: \n === {all_messages}')
        response = self.character_model(messages=all_messages)
        content = response.content
        if self.dialogue_manager.check_dialogue():
            client.pop(list_name)

        back_dialogue = self.dialogue_manager.add_dialogue(role_from=self.id, role_to=player_id, content=content, content_type=content_type)
        client.push(list_name, call_dialogue)
        client.push(list_name, back_dialogue)
        return content

@dataclass
class Scene(Base):
    __tablename__ = 'scene'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    scene = Column(Text)
    theater = Column(Text)
    theater_event = Column(Text)
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'scene': self.scene,
            'theater': self.theater,
            'theater_event': self.theater_event,
            'roles': self.roles,
            'score': self.score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class NPCManager:
    def __init__(self, mysql_client: MySQLDatabase, redis_client: RedisList):
        self.mysql_client = mysql_client
        self.redis_client = redis_client
        self._instances = {}        
        
        npc_users = self.mysql_client.select_all_records(record_class=NPCUser)
        for npc_user in npc_users:
            new_npc_user = NPCUser(id=npc_user.id, 
                                   name=npc_user.name, 
                                   npc_id=npc_user.npc_id, 
                                   user_id=npc_user.user_id, 
                                   sex=npc_user.sex, 
                                   score=npc_user.score,
                                   trait=npc_user.trait, 
                                   scene=npc_user.scene,
                                   )
            new_npc_user.init(redis_client=redis_client)
            debuglog.info(f'npc_user init: new npc_user === {new_npc_user.to_dict()}')
            self._instances[npc_user.id] = new_npc_user

    def get_npcs(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[NPC]:
        npcs = self.mysql_client.select_records(record_class=NPC, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return npcs
    
    def get_npc(self, npc_id) -> NPC:
        filter_dict = {'id': npc_id}
        npc = self.mysql_client.select_record(record_class=NPC, filter_dict=filter_dict)
        return npc
    
    def update_npc(self, npc: NPC)->NPC:
        new_npc = self.mysql_client.update_record(npc)
        debuglog.info(f'update_npc: new npc === {new_npc.to_dict()}')
        filter_dict = {'npc_id': npc.id}
        npc_user_list = self.mysql_client.select_records(record_class=NPCUser, filter_dict=filter_dict)
        debuglog.info(f'update_npc: npc_user list len === {len(npc_user_list)}')
        for npc_user in npc_user_list:
            npc_user_id = npc_user.id
            old_npc_user = self._instances.get(npc_user_id, None)
            old_npc_user.name = new_npc.name
            old_npc_user.sex = new_npc.sex
            old_npc_user.trait = new_npc.trait
            self._instances[npc_user_id] = old_npc_user
            debuglog.info(f'update_npc: update npc and update cache npc_user = {old_npc_user.to_dict()}')

            npc_user.name = new_npc.name
            npc_user.sex = new_npc.sex
            npc_user.trait = new_npc.trait
            db_npc_user = self.mysql_client.update_record(npc_user)
            debuglog.info(f'update_npc: update npc and update db npc_user = {db_npc_user}')
        return new_npc

    def remove_npc(self, npc_id: str):
        self.mysql_client.delete_record_by_id(NPC, npc_id)
    
    def set_npc(self, name: str, sex: int, trait: str, short_description: str,
                               prompt_description: str, profile: str, chat_background: str, affinity_level_description: str)->NPC:
        new_npc= NPC(name=name, sex=sex, trait=trait, short_description=short_description,
                               prompt_description=prompt_description, profile=profile, chat_background=chat_background, affinity_level_description=affinity_level_description)
        new_npc = self.mysql_client.insert_record(new_npc)
        return new_npc
    
    def get_npc_user(self, npc_id: str, user_id: str) -> NPCUser:
        npc_user_id = f'{npc_id}_{user_id}'
        npc_user = self._instances.get(npc_user_id, None)
        return npc_user

    def get_npc_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[NPCUser]:
        npc_users = self._instances.values()
        npc_user_list = list(npc_users)

        if filter_dict:
            for attr, value in filter_dict.items():
                npc_user_list = [npc_user for npc_user in npc_user_list if getattr(npc_user, attr) == value]

        if order_by:
            for attr, ascending in order_by.items():
                npc_user_list.sort(key=lambda user: getattr(user, attr), reverse=not ascending)

        start_index = (page - 1) * limit
        end_index = start_index + limit
        new_npc_user_list = npc_user_list[start_index:end_index]
        return new_npc_user_list
    
    def get_npc_all_info(self, npc_id: str, user_id: str) -> dict:
        npc_user_id = f'{npc_id}_{user_id}'
        npc_user = self._instances.get(npc_user_id, None)
        npc = self.get_npc(npc_id)
        if npc_user != None and npc != None:
            dict_1 = npc.to_dict()
            dict_2 = npc_user.to_dict()
            merged_dict = {**dict_2, **dict_1}
            return merged_dict
        if npc_user == None and npc != None:
            dict_1 = npc.to_dict()
            dict_1['scene'] = "宅在家里"
            return npc.to_dict()
        return None

    
    def create_npc_user(self, name:str, npc_id:str, user_id:str, trait:str, scene: str, sex: int) -> NPCUser:
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识不久，虽然互有好感，但彼此之间还不太熟悉，在他面前你的表现是「害羞、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，并相互暧昧，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、挑逗、调侃」。",
            friend="你们已经是亲密关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「主动、渴望、黏人、撒娇」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间心有灵犀，和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        affinity = AffinityManager(score=60, level=affinity_level)
        dialogue_context = []
        npc_user_id = f'{npc_id}_{user_id}'
        new_npc_user = NPCUser(id=npc_user_id, name=name, npc_id=npc_id, user_id=user_id, sex=sex, trait=trait, scene=scene, affinity=affinity, dialogue_context=dialogue_context)
        self.mysql_client.insert_record(new_npc_user)
        self._instances[npc_user_id] = new_npc_user
        return new_npc_user