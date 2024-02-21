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
            name="IncreaseAffinity",
            description="""基于对话内容，让角色增加好感度""",
            parameters={
                "properties": {
                    "amount": {"description": "参数为整型，表示增加好感度的数值，增加幅度在0-5，其中1表示好感度轻微提升，5表示好感度大幅提升", "type":"string"}
                    },
                    "required": ["amount"],
                    "type": "object",
            },
        )
        funtioncall_decrease_affinity = doubao.ModelFunctionClass(
            name="DecreaseAffinity",
            description="""基于对话内容，让角色减少好感度，传入一个整数""",
            parameters={
                "properties": {
                    "amount": {"description": "参数为整型，表示减少好感度的数值，减少幅度在0-5，其中1表示好感度轻微减少，5表示好感度大幅减少", "type":"string"}
                    },
                    "required": ["amount"],
                    "type": "object",
            },
        )
        self.model = doubao.ChatSkylark(
            model="skylark2-pro-4k",
            model_version="1.100",
            model_endpoint="mse-20231227193502-58xhk",
            top_k=1,
            functions=[funtioncall_increase_affinity, funtioncall_decrease_affinity]
        )
        # 好感计算提示词
        self.system_prompt = '''你是一位情感分析师，可以根据对人物性格的解析和对话内容以确定好感度的变化。'''

    def increase_affinity(self, amount):
        """增加好感度"""
        self.score += amount

    def decrease_affinity(self, amount):
        """减少好感度"""
        self.score -= amount
    
    def get_score(self):
        return self.score
    
    def get_relation_level(self)->str:
        return self.affinity_level.get_level_description(self.score)
    
    def calculate_affinity(self, npc:str, target:str, history_dialogues:str, dialogue_content:str)->None:
        affinity_level = self.affinity_level.get_level(self.score)
        affinity_analysis = f"""你任务是分析{npc}对{target}的好感变化，当前好感是：\n{affinity_level}\n，下面是他们的对话:\n{history_dialogues}\n现在{target}对{npc}说: "{dialogue_content}"，{npc}的好感度会怎么样"""
        all_messages = [SystemMessage(content=self.system_prompt),HumanMessage(content=affinity_analysis)]
        print(all_messages)
        result = self.model(messages=all_messages)
        if "function_call" in result.additional_kwargs:
            fn_name = result.additional_kwargs["function_call"]["name"]
            fn_params = result.additional_kwargs["function_call"]["arguments"]
            fn_params = json.loads(fn_params)
            amount = int(fn_params["amount"])
            if fn_name == "IncreaseAffinity":
                self.increase_affinity(amount)
            if fn_name == "DecreaseAffinity":
                self.decrease_affinity(amount)
        else:
            print("好感无变化.\n%s"%result.content)
    
    def __str__(self):
        """返回好感度的字符串表示"""
        return "当前好感度为: %s。\n关系表现: %s"%(self.score,self.get_relation_level())