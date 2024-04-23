# coding:utf-8
"""
npc's emotion module.
author: shikanon
create: 2024/1/21
"""
import json
from typing import List
from gamenpc.utils.logger import debuglog
from langchain.schema import SystemMessage, HumanMessage
from gamenpc.model import doubao

# class AffinityLevelDescription:
#     '''好感等级：
#     acquaintance:初识(0-10)
#     familiar:熟人(10-30)
#     friend:亲密朋友(30-70)
#     soulmate:心灵伴侣(70-100)
#     adversary:敌对(<0)
#     '''
#     def __init__(self, acquaintance:str, familiar:str, friend:str, soulmate:str, adversary:str) -> None:
#         self.acquaintance = acquaintance
#         self.familiar = familiar
#         self.friend = friend
#         self.soulmate = soulmate
#         self.adversary = adversary
#         self.adversary_upper_bound = 0
#         self.acquaintance_upper_bound = 10
#         self.familiar_upper_bound = 30
#         self.friend_upper_bound = 70
#         self.soulmate_upper_bound = 100
#         self.status = "acquaintance"
#         self.status = "familiar"
#         self.status = "friend"
#         self.status = "soulmate"

#     def get_level_status(self,score)->str:
#         if score < self.adversary_upper_bound:
#             self.status = "adversary"
#         elif score >= self.adversary_upper_bound and score < self.acquaintance_upper_bound:
#             self.status = "acquaintance"
#         elif score >= self.acquaintance_upper_bound and score < self.familiar_upper_bound:
#             self.status = "familiar"
#         elif score >= self.familiar_upper_bound and score <self.friend_upper_bound:
#             self.status = "friend"
#         else:
#             self.status = "soulmate"
#         return self.status
    
#     def get_level_description(self,score)->str:
#         self.get_level_status(score)
#         if self.status == "adversary":
#             return self.adversary
#         if self.status == "acquaintance":
#             return self.acquaintance
#         if self.status == "familiar":
#             return self.familiar
#         if self.status == "friend":
#             return self.friend
#         if self.status == "soulmate":
#             return self.soulmate
    
        
class Affinity:
    def __init__(self, level=0, affinity_rules=None) -> None:
        self.level = level
        if affinity_rules == None:
            affinity_rules = [
                {
                    "lv": 1,
                    "content": "你们刚刚认识不久，虽然互有好感，但彼此之间还不太熟悉，在他面前你的表现是「害羞、好奇、试探」。",
                    "score": 0
                },
                {
                    "lv": 2,
                    "content": "你们经过长时间交流，已经相互有深度的了解，并相互暧昧，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、挑逗、调侃」。",
                    "score": 20
                },
                {
                    "lv": 3,
                    "content": "你们已经是亲密关系，你在他面前你的表现是「主动、渴望、黏人、撒娇」。",
                    "score": 40
                },
                {
                    "lv": 4,
                    "content": "你们已经是亲密关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「主动、渴望、黏人、撒娇」。",
                    "score": 60
                },
                {
                    "lv": 5,
                    "content": "你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间心有灵犀，和谐到了几乎完美的境界，你们互信互依。",
                    "score": 100
                }
            ]
        else:
            affinity_rules = [rule_data.__dict__ for rule_data in affinity_rules]
        
        # 按照 AffinityRule 的 score 属性排序
        sorted_affinity_rules = sorted(affinity_rules, key=lambda rule: rule['score'])
        self.current_rule = sorted_affinity_rules[self.level]
        self.affinity_rules = sorted_affinity_rules

    def calculate_current_rule(self, score: int):
        rules = self.affinity_rules
        # 边际条件处理
        if score < rules[0]['score']:
            return rules[0]['lv']
        if score > rules[-1]['score']:
            return rules[-1]['lv']
            
        # 寻找适合的lv
        rule = rules[0]
        for index in range(1, len(rules)):
            if score < rules[index]['score']:
                break
            rule = rules[index]
        self.current_rule = rule
        return rule
    
    def get_score_affinity_level_description(self, score: int) -> str:
        rule = self.calculate_current_rule(score=score)
        print('rule: ========', rule)
        if rule != None and rule['content'] != None:
            return rule['content']
        return ''
        
    def get_score_affinity_level(self, score: int) -> int:
        rule = self.calculate_current_rule(score=score)
        print('rule: ========', rule)
        if rule != None and rule['lv'] != None:
            return rule['lv']
        return 0

class AffinityManager:
    def __init__(self, score: int, affinity: Affinity) -> None:
        self.score = score
        self.affinity = affinity
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
        self.system_prompt = '''你是一位情感洞察师，可以根据对人物性格的解析和对话内容以确定好感度的变化。'''

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
    
    def get_affinity_level(self)->int:
        return self.affinity.get_score_affinity_level(self.score)
    
    def get_affinity_level_description(self)->str:
        return self.affinity.get_score_affinity_level_description(self.score)
    
    def calculate_affinity(self, npc:str, target:str, history_dialogues:str, dialogue_content:str)->None:
        affinity_level_description = self.get_affinity_level_description()
        affinity_analysis = f"""你任务是分析{npc}对{target}的好感变化，当前好感是：\n{affinity_level_description}\n，下面是他们的对话:\n{history_dialogues}\n现在{target}对{npc}说: "{dialogue_content}"，{npc}对{target}的好感度是增加还是减少，增加调用IncreaseAffinity函数，减少调用DecreaseAffinity"""
        all_messages = [SystemMessage(content=self.system_prompt),HumanMessage(content=affinity_analysis)]
        debuglog.info(f'calculate_affinity: all_messages === {all_messages}')
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
            debuglog.info("好感无变化.\n%s"%result.content)
    
    def __str__(self):
        """返回好感度的字符串表示"""
        return "当前好感度为: %s。\n关系表现: %s"%(self.score, self.get_affinity_level_description())
