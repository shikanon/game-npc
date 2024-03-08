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

# from gamenpc import memory
from gamenpc.memory.memory import Mind, DialogueMemory, DialogueEntry
from gamenpc.model import doubao
from gamenpc.emotion import AffinityManager, AffinityLevel
from gamenpc.store import MySQLDatabase


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

class NPC_config:
    '''
    NPC配置, 暂时两个字段
    '''
    def __init__(self, 
                 id:str, 
                 name:str, 
                 trait:str, 
                 description:str, 
                 updated_at:str, 
                 )->None:
        self.id = id
        self.name = name
        self.trait = trait
        self.description = description
        self.updated_at = updated_at
    def __len__(self):
        # 在这里定义对象的长度
        return 5  # 假设这里的长度为2，表示两个字段
    def keys(self):
        return ['id', 'name', 'trait', 'description', 'updated_at']
    def values(self)->List:
        values = []
        values.append(self.id)
        values.append(self.name)
        values.append(self.trait)
        values.append(self.description)
        values.append(self.updated_at)
        return values

class NPC:
    '''
    NPC名称、角色prompt模板、好感系统、场景
    '''
    def __init__(self, 
                 id:str,
                 name:str,
                 user_name:str,  
                 trait:str, 
                 dialogue_context:List,
                 affinity:AffinityManager, 
                 scene='',
                 role_template_filename='',
                 dialogue_summarize_num=20,
                 dialogue_round=6,
                 )->None:
        self.id = id
        self.name = name
        self.user_name = user_name
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
        self.thoughts = Mind(model=model, character=trait)
        self.dialogue_manager = DialogueMemory(dialogue_context=dialogue_context, mind=self.thoughts, summarize_limit=dialogue_summarize_num)
        # character model
        self.character_model = doubao.ChatSkylark(
            model="skylark2-pro-character-4k",
            top_k=1,
        )

    def __len__(self):
        # 在这里定义对象的长度
        return 6  # 假设这里的长度为2，表示两个字段
    
    def keys(self)->List:
        return ['id', 'name', 'user_name', 'trait', 'score', 'affinity_level']

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

    async def chat(self, client: MySQLDatabase, player_name:str, message:str)->str:
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
        self.dialogue_manager.add_dialogue(client=client, role_from=player_name, role_to=self.name, content=message)
    
        response = self.character_model(messages=all_messages)
        anwser = response.content
        self.dialogue_manager.add_dialogue(client=client, role_from=self.name, role_to=player_name, content=anwser)

        return anwser



class NPCManager:
    def __init__(self, client: MySQLDatabase):
        self.client = client
        self._instances = {}
        records = self.client.select_records("npcs")
        for record in records:
            npc_id = record[0]
            name = record[1]
            user_name = record[2]
            traits = record[3]
            score = record[4]
            scene = record[5]
            affinity_level = AffinityLevel(
                acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
                familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
                friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
                soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
                adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
            )
            affinity = AffinityManager(score=score,level=affinity_level)
            # db中加载历史对话
            dialogue_context = []
            dialogue_records = self.client.select_records("dialogues")
            for dialogue_record in dialogue_records:
                dialogue_id = dialogue_record[0]
                dialogue_role_from = dialogue_record[1]
                dialogue_role_to = dialogue_record[2]
                dialogue_content = dialogue_record[3]
                dialogue_context.append(DialogueEntry(dialogue_id, dialogue_role_from, dialogue_role_to, dialogue_content))
            self._instances[npc_id] = NPC(id=npc_id, name=name, user_name=user_name, 
                                             trait=traits, scene=scene, affinity=affinity, dialogue_context=dialogue_context)
        self._instance_configs = {}
        records = self.client.select_records("npc_configs")
        for record in records:
            name = record[0]
            traits = record[1]
            self._instance_configs[name] = NPC_config(name=name, trait=traits)
        print('self._instance_configs: ', self._instance_configs)

    def get_npc(self, user_name: str, npc_name: str) -> NPC:
        npc_id = user_name + '_' + npc_name
        # if npc_id not in self._instances:
        #     raise ValueError('NPC %s not Exist.'%npc_id)
        return self._instances.get(npc_id)

    def get_npc_config(self, npc_name: str) -> NPC_config:
        npc_config = self._instance_configs.get(npc_name)
        return npc_config
    
    def get_all_npc_config(self) -> list:
        instance_config_list = []
        for name in self._instance_configs:
            instance_config_list.append(self._instance_configs[name])
        return instance_config_list
    
    def set_npc_config(self, npc_name: str, npc_traits: str):
        new_npc_config= NPC_config(name=npc_name, trait=npc_traits)
        self.client.insert_record("npc_configs", new_npc_config)
        self._instance_configs[npc_name] = new_npc_config
    
    def create_npc(self, user_name:str, npc_name:str, npc_traits:str, scene: str) -> NPC:
        affinity_level = AffinityLevel(
            acquaintance="你们刚刚认识，彼此之间还不太熟悉，在他面前你的表现是「谨慎、好奇、试探」。",
            familiar="你们经过长时间交流，已经相互有深度的了解，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、真诚、调侃」。",
            friend="你们是亲密朋友关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「关爱、感激、深情、溺爱」。",
            soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间理解和和谐到了几乎完美的境界，你们互信互依。",
            adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
        )
        affinity = AffinityManager(score=0,level=affinity_level)
        npc_id = user_name + '_' + npc_name
        dialogue_context = []
        self._instances[npc_id] = NPC(id=npc_id, name=npc_name, user_name=user_name, trait=npc_traits, scene=scene, affinity=affinity, dialogue_context=dialogue_context)
        # affinity_json = json.dumps(affinity.__dict__)
        npc = {"id": npc_id, "name": npc_name, "user_name": user_name, "trait": npc_traits, "score":0, "scene": scene, "affinity_level": 100}
        self.client.insert_record("npcs", npc)
        return self._instances.get(npc_id)