# coding:utf-8
import time
import datetime
import asyncio
import re
from collections import deque
from typing import List
from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from gamenpc.store.mysql_client import Base
from gamenpc.store.redis_client import RedisList
import uuid
from gamenpc.utils.logger import debuglog

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from dataclasses import dataclass

# debuglog = DebugLogger("memory")

CONTENT_TYPE_TEXT = "text"
CONTENT_TYPE_IMAGE = "image"

summarize_dialogue_template = """
# 角色
{character}

## 技能
### 技能1：场景描述
- 根据提供的对话内容，进行场景描述，描述其中的人物行为以及他们的反应。

### 技能2：心情表达
- 根据场景内容，描述你的心情，包括欢喜、惊愕、忧郁、疑惑、安宁、怜爱、羞怯。

### 技能3：心情原因解释
- 阐述产生当前心情的原因。

## 限制
- 强调场景描述的细节。
- 心情需要具体化，不要使用模糊不清的词语。
- 心情原因需要详细解释，解释出为什么你会有这样的心情。

## 回答要求
### 回答格式
你的回答应该包含以下格式：
```
scenes:  描述场景，包括谁在做什么，大家对此的看法是什么。
emotion: 描述你的心情，包含欢喜、惊愕、忧郁、疑惑、安宁、怜爱、羞怯。
reason:  使用第一人称阐述产生这种情绪的原因。
```

### 回复示例
以下是一个符合回答格式的示例：
```
scenes:  在广播部的活动中，我的优雅的声音引人注目，到场的学生们对我的声音称赞有加。特别是学长市村龙之介，他的赞美和安慰让我感到意外的惊喜和害羞。
emotion: 羞怯
reason:  市村龙之介赞美我有独特而动人的声音时，我感到羞怯又欣喜。尤其是在他的赞美面前，我感到我内心充满了复杂的情感。
```
"""


event_template = """
# 角色
{character}

## 技能
### 技能1: 事情的决定性评估
- 对事情的重要程度进行评估，按照0分（最不重要）至10分（最重要）的标准进行评级。
- 0-3分可以用来判断一些琐事或者情绪的波动，如轻松闲聊、流言蜚语或者日常洗漱等。
- 4-7分用于评定可能会对你日常生活造成影响的事件，如工作环境的改变或者和朋友约会。
- 8-10分用来评级那些可能会改变你人生方向的大事件，如婚礼或者离别。

### 技能2: 事件分类
- 将事件按照其性质分为五种类型：日常琐事、社交关系变化、个人成长、工作事件、关键人生事件。

## 答复规定
### 答复格式
请照着以下的格式来答复：
```
event: <具体事情>，什么时间，谁做了什么。
type: <事件类型>
score: <事件的重要程度>，用0分到10分来判断。
reason: <为何给出这个评分>，这个事件对你来说是否重要，以及为什么。
```

### 回答示例
下面是一个回答例子，遵循以上的格式：
```
event: 2月1日，小A向你告白，你俩开始了恋爱关系。
type: 社交关系变化
score: 8
reason: 小A是你一直暗恋的人，他向你告白，你们终于在一起了，因此对你来说这是一件非常重要的事情，它对你的人生轨迹产生了重大影响。
```

## 约束
- 坚持使用提供的输出格式。
- 尽量用角色知道的信息回答问题。 
"""

@dataclass
class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    npc_id = Column(String(255), ForeignKey('npc.id'))  # NPC对象，外键
    #关联NPC对象
    npc = relationship('NPC')
    theater = Column(String(255))  # 剧情章节
    theater_event = Column(String(255))  # 剧情的事件（JSON）
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

    def __init__(self, npc_id=None, theater=None, theater_event=None):
        self.npc_id = npc_id
        self.theater = theater
        self.theater_event = theater_event

    def to_dict(self):
        return {
            'id': self.id,
            'npc_id': self.npc_id,
            'theater': self.theater,
            'theater_event': self.theater_event,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }

@dataclass
class DialogueEntry(Base):
    __tablename__ = 'dialogue'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    role_from = Column(Integer)  # 消息发出对象ID
    role_to = Column(Integer)  # 消息接收对象ID
    content = Column(String(255))  # 消息内容
    content_type = Column(String(255))  # 内容类型
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

    '''对话实体，谁说了什么话'''
    def __init__(self, role_from:str, role_to:str, content:str, content_type:str):
        self.id = str(uuid.uuid4())
        self.role_from = role_from
        self.role_to = role_to
        self.content = content  # 存储对话内容
        # 类型：text, image
        if content_type in [CONTENT_TYPE_TEXT, CONTENT_TYPE_IMAGE]:
            self.content_type = content_type 
        else:
            self.content_type = CONTENT_TYPE_TEXT
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'role_from': self.role_from,
            'role_to': self.role_to,
            'content': self.content,
            'content_type': self.content_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
    
    def __str__(self) -> str:
        '''处理对话，加入外部变量'''
        speaker = self.role_from
        message = self.content
        if self.created_at == None:
            self.created_at = datetime.now()
        created_at = self.created_at.strftime("%A %B-%d %X"), 
        content = "%s: %s"%(speaker, message)
        return content

@dataclass
class ConverationEntry:
    '''会话场景'''
    def __init__(self, scene:str, emotion:str, emotion_reason:str) -> None:
        self.scene = scene
        if emotion in ["欢喜","惊愕","忧郁","疑惑","安宁","怜爱","羞怯"]:
            self.emotion = emotion
        else:
            self.emotion = "未知"
        self.reason = emotion_reason
        self.context = ""
    
    def add_context(self, dialogue_context:str)->None:
        self.context = dialogue_context
    
    def get_scene(self)->str:
        return self.scene
    
    def get_emotion(self)->str:
        return self.emotion
    
    def get_emotion_reason(self)->str:
        return self.reason
    
    def get_context(self)->str:
        return self.context
    
    def __str__(self) -> str:
        return "场景：%s\n 心情：%s\n 情绪原因：%s"%(self.scene, self.emotion, self.reason)


@dataclass
class TopicEvent:
    '''主题事件'''
    def __init__(self, content:str, event_type:str, score:int, reason:str) -> None:
        self.content = content
        self.event_type = event_type
        self.score = score
        self.reason = reason
        self.set_keyevent()
    
    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score

    def set_keyevent(self):
        if self.score >= 8 :
            self.key = True
        else:
            self.key = False
    
    def is_keyevent(self):
        return self.key
    
    def __str__(self) -> str:
        if self.key:
            return "[关键事件]：%s"%self.content
        return self.content

@dataclass
class Mind:
    '''
    转换关系：DialogueEntry -> Converation -> TopicEvent
    '''
    def __init__(self,model:BaseChatModel, character:str):
        self.model = model
        self.character = character
        self.dialogue_system_prompt = SystemMessagePromptTemplate.from_template(
            template=summarize_dialogue_template,
        ).format(character=character)
        self.event_system_prompt = SystemMessagePromptTemplate.from_template(
            template=event_template,
        ).format(character=character)
    
    async def summarize_dialogue2converation(self,dialogues:List[DialogueEntry])->ConverationEntry:
        # 将对话内容总结成会话
        dialog = "\n".join(str(dia) for dia in dialogues)
        messages = [self.dialogue_system_prompt,HumanMessage(content=dialog)]
        response = self.model(messages)
        result = response.content
        # 按指定格式解析大模型的输出
        if "scenes:" in result:
            scene = re.search(r'scenes:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            scene = "模型未按照指定格式输出"
        if "emotion:" in result:
            emotion = re.search(r'emotion:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            emotion = ""
        if "reason:" in result:
            reason = re.search(r'reason:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            reason = "模型未按照指定格式输出"
        entry = ConverationEntry(scene=scene,emotion=emotion,emotion_reason=reason)
        entry.add_context(dialog)
        return entry
    
    async def summarize_converation2event(self, converation:List[ConverationEntry])->TopicEvent:
        # 将会话总结成事件，并给得分
        all_conversation = "\n\n".join(c.get_scene()+'\n'+c.get_context() for c in converation)
        messages = [
            self.event_system_prompt, HumanMessage(content=all_conversation)
        ]
        response = self.model(messages)
        result = response.content
        # 按指定格式解析大模型的输出
        if "event:" in result:
            event_content = re.search(r'event:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            event_content = "模型未按照指定格式输出"
        if "type:" in result:
            event_type = re.search(r'type:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            event_type = "日常琐事"
        if "score:" in result:
            score = re.search(r'score:(\d+)', result).group(1)
            score = int(score)
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            score = 0
        if "reason:" in result:
            reason = re.search(r'reason:(.*?)(?=\n|$)', result).group(1).strip()
        else:
            # 大模型未按照指定格式输出，则给默认字段用于定位
            reason = "模型未按照指定格式输出"
        event = TopicEvent(content=event_content, event_type=event_type, score=score, reason=reason)
        return event

@dataclass
class DialogueMemory:
    def __init__(self, dialogue_context:List[DialogueEntry], mind:Mind, summarize_limit=10, max_dialogue_history=100):
        self.mind = mind
        # 对话上下文
        self.dialogue_context = dialogue_context  
        # 最大存储的对话上下文数量，超出则从头部删除
        self.context_limit = max_dialogue_history
        # 会话，上下文的总结
        self.conversation = []
        # 计数器，每个会话由多个对话对组成
        self.summarize_limit = summarize_limit
        self.dialogue_pair_count = 0

    def to_dict(self):
        return {
            'mind': self.mind,
            'dialogue_context': self.dialogue_context,
            'context_limit': self.context_limit,
            'conversation': self.conversation,
            'summarize_limit': self.summarize_limit,
            'dialogue_pair_count': self.dialogue_pair_count,
        }
    
    def check_dialogue(self)-> bool:
        flag = False
        if self.dialogue_context == None:
            return flag
        if len(self.dialogue_context) >= self.context_limit:
            # 移除最早的上下文以便为新上下文腾出空间; 同时清理数据库中的信息。
            self.dialogue_context.pop(0)
            flag = True
        return flag
    
    def add_dialogue(self, role_from, role_to, content, content_type)->DialogueEntry:
        dialogue =  DialogueEntry(role_from=role_from, role_to=role_to, content=content, content_type=content_type)
        # 历史对话持久化到db中
        self.dialogue_context.append(dialogue)
        debuglog.info(f'add_dialogue: dialogue_context ===== {[dialogue.to_dict() for dialogue in self.dialogue_context]}')
        self.dialogue_pair_count = self.dialogue_pair_count + 1

        # 如果新增会话大于阈值，对会话内容进行总结
        if self.dialogue_pair_count > self.summarize_limit:
            # 异步做总结可以不阻塞对话过程，保证延迟体验
            # 使用list重新生成一个新对象来防止dialogue_context的修改影响recent_dialogues
            recent_dialogues = list(self.dialogue_context[-self.summarize_limit:])
            debuglog.info(f'add_dialogue: recent_dialogues list === {[dialogue.to_dict() for dialogue in recent_dialogues]}')
            asyncio.create_task(self.add_summary(recent_dialogues))
            # 重置对话长度
            self.dialogue_pair_count = 0

        return dialogue
    
    def new_dialogue(self, role_from, role_to, content, content_type)->DialogueEntry:
        dialogue =  DialogueEntry(role_from=role_from, role_to=role_to, content=content, content_type=content_type)
        return dialogue

    def get_recent_dialogue(self, round=6)->str:
        '''返回最新的上下文，并进行格式化输出
        '''
        output_diglogue = ""
        for ctx in self.dialogue_context:
            if ctx.content_type == CONTENT_TYPE_TEXT:
                output_diglogue = output_diglogue + str(ctx)
        return output_diglogue

    def get_all_contexts(self)->List[DialogueEntry]:
        # 返回所有上下文，按时间顺序排列
        return self.dialogue_context
    
    def set_contexts(self, dialogue_context: List[DialogueEntry]):
        # 返回所有上下文，按时间顺序排列
        self.dialogue_context = dialogue_context
    
    async def add_summary(self, dialogues: List[DialogueEntry]):
        # 异步函数，生成对话总结
        summary = await self.mind.summarize_dialogue2converation(dialogues)
        debuglog.info(f'add_summary: summary === {summary}')
        self.conversation.append(summary)
    
    def get_recent_conversation(self, round=1)->List[ConverationEntry]:
        # 返回最新的会话总结
        return self.conversation[-round:] if self.conversation else None
    
    def get_all_conversation(self)->List[ConverationEntry]:
        return self.conversation
    
    def clear(self, redis_client: RedisList, npc_user_id)->None:
        # 清空db数据
        list_name = f'dialogue_{npc_user_id}'
        redis_client.delete(list_name)    
        self.dialogue_context = []
        self.conversation = []
        self.dialogue_pair_count = 0

    def gen_topic_event(self)->TopicEvent:
        conversation = self.get_all_conversation()
        if conversation:
            return self.mind.summarize_converation2event(conversation)
        else:
            return None
    