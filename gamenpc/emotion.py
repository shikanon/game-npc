# coding:utf-8
"""
npc's emotion module.
author: shikanon
create: 2024/1/21
"""
import json
from typing import Dict, List
from langchain.schema import SystemMessage, HumanMessage

from gamenpc.model import doubao

class AffinityLevel:
    '''好感等级：
    acquaintance:初识(0-10)
    familiar:熟人(10-30)
    friend:亲密朋友(30-70)
    soulmate:心灵伴侣(70-100)
    adversary:敌对(<0)
    '''
    def __init__(self, acquaintance:str, familiar:str, friend:str, soulmate:str, adversary:str) -> None:
        self.acquaintance = acquaintance
        self.familiar = familiar
        self.friend = friend
        self.soulmate = soulmate
        self.adversary = adversary
        self.adversary_upper_bound = 0
        self.acquaintance_upper_bound = 10
        self.familiar_upper_bound = 30
        self.friend_upper_bound = 70
        self.soulmate_upper_bound = 100
        self.status = "acquaintance"
        self.status = "familiar"
        self.status = "friend"
        self.status = "soulmate"

    def get_level(self,score)->str:
        if score < self.adversary_upper_bound:
            self.status = "adversary"
        elif score >= self.adversary_upper_bound and score < self.acquaintance_upper_bound:
            self.status = "acquaintance"
        elif score >= self.acquaintance_upper_bound and score < self.familiar_upper_bound:
            self.status = "familiar"
        elif score >= self.familiar_upper_bound and score <self.friend_upper_bound:
            self.status = "friend"
        else:
            self.status = "soulmate"
        return self.status
    
    def get_level_description(self,score)->str:
        self.get_level(score)
        if self.status == "adversary":
            return self.adversary
        if self.status == "acquaintance":
            return self.acquaintance
        if self.status == "familiar":
            return self.familiar
        if self.status == "friend":
            return self.friend
        if self.status == "soulmate":
            return self.soulmate

class AffinityManager:
    def __init__(self, score:int, level:AffinityLevel) -> None:
        self.score = score
        self.affinity_level = level
        # 定义模型
        funtioncall_increase_affinity = doubao.ModelFunctionClass(
            name="improve_favorability",
            description="""增加角色对玩家好感度的方法""",
            parameters={
                "properties": {
                    "reason": {"description": "从多个角度解释调用该方法的详细原因", "type":"string"},
                    "amount": {"description": "参数为整型，表示提升好感度的数值，提升幅度在-5到5之间，其中1表示好感度轻微提升，5表示好感度大幅提升", "type":"string"},
                    },
                    "required": ["amount"],
                    "type": "object",
            },
        )
        funtioncall_decrease_affinity = doubao.ModelFunctionClass(
            name="reduce_favorability",
            description="""降低角色对玩家好感度的方法""",
            parameters={
                "properties": {
                    "reason": {"description": "从多个角度解释调用该方法的详细原因", "type":"string"},
                    "amount": {"description": "参数为整型，表示降低好感度的数值，降低幅度在-5到5之间，其中1表示好感度轻微降低，5表示好感度大幅降低", "type":"string"},
                    },
                    "required": ["amount"],
                    "type": "object",
            },
        )
        funtioncall_no_change = doubao.ModelFunctionClass(
            name="no_change",
            description="""好感度没有变化""",
            parameters={
                "properties": {
                    "reason": {"description": "从多个角度解释调用该方法的详细原因", "type":"string"}
                    },
                    "type": "object",
            },
        )
        self.model = doubao.ChatSkylark(
            model="skylark2-pro-4k",
            model_version="1.2",
            top_k=1
        )
        self.fn_model = doubao.ChatSkylark(
            model="skylark2-pro-4k",
            model_version="1.100",
            model_endpoint="mse-20231227193502-58xhk",
            top_k=1,
            functions=[funtioncall_increase_affinity, funtioncall_decrease_affinity, funtioncall_no_change]
        )
        # 好感计算提示词
        self.analysis_system_prompt = '''# 角色
你是一位情感洞察师，可以根据对人物性格的解析和对话内容以确定好感度的变化，要从角色深层想法去分析，结合场景说明为什么会变化，是大幅变化还是几乎没有变化。

# 技能：分析角色情感变化原因
1. 根据对人物性格和对话内容的分析，确定人物之间的好感度变化。通过观察和分析人物的言行举止、情感表达、人际关系等方面，了解人物的性格特点，分析对话中人物的语言、语气、态度等因素，了解人物的情感和想法，说明好感度变化的原因。
2. 判断好感度变化的幅度，是大幅增加或减少，还是几乎没有变化。
3. 不做过多假设和猜测。'''
        

    def increase_affinity(self, amount):
        """增加好感度"""
        self.score += amount

    def decrease_affinity(self, amount):
        """减少好感度"""
        self.score -= amount
    
    def get_score(self):
        return self.score
    
    def set_score(self, score:int):
        self.score = score
        return self.score
    
    def get_relation_level(self)->str:
        return self.affinity_level.get_level_description(self.score)
    
    def calculate_affinity(self, npc:str, target:str, history_dialogues:str, dialogue_content:str)->None:
        affinity_level = self.affinity_level.get_level(self.score)
        affinity_analysis_messages = [
            SystemMessage(content=self.analysis_system_prompt),
            HumanMessage(content=f"{history_dialogues}\n\n他们的关系是{affinity_level} \n分析{dialogue_content}这句话对角色好感的影响及原因")
        ]
        affinity_analysis_result = self.model(messages=affinity_analysis_messages)
        affinity_analysis = affinity_analysis_result.content
        print(affinity_analysis)
        self.functioncall_system_prompt = f'''你是一个NPC角色好感系统控制器，负责调节角色好感的高低。基于NPC（{npc}）对玩家（{target}）的好感度变化调节NPC好感度'''
        functioncall_messages = [SystemMessage(content=self.functioncall_system_prompt),HumanMessage(content=affinity_analysis)]
        result = self.fn_model(messages=functioncall_messages)
        if "function_call" in result.additional_kwargs:
            fn_name = result.additional_kwargs["function_call"]["name"]
            fn_params = result.additional_kwargs["function_call"]["arguments"]
            fn_params = json.loads(fn_params)
            print(result)
            print(fn_name,fn_params)
            amount = int(fn_params["amount"])
            if fn_name == "improve_favorability":
                self.increase_affinity(amount)
            if fn_name == "reduce_favorability":
                self.decrease_affinity(amount)
        else:
            print("好感无变化.\n%s"%result.content)
    
    def __str__(self):
        """返回好感度的字符串表示"""
        return "当前好感度为: %s。\n关系表现: %s"%(self.score,self.get_relation_level())
