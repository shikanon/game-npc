# coding:utf-8
"""
npc's emotion module.
author: shikanon
create: 2024/1/21
"""
import json
from gamenpc.utils.logger import debuglog
from langchain.schema import SystemMessage, HumanMessage
from gamenpc.model import doubao

class AffinityLevelDescription:
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

    def get_level_status(self,score)->str:
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
    
        
class Affinity:
    def __init__(self, level=0, description=None, upper_bound={
        'lv0': 0,
        'lv1': 10,
        'lv2': 30,
        'lv3': 70,
        'lv4': 100,
    }) -> None:
        self.level = level
        if description == None:
            description = AffinityLevelDescription(
                acquaintance="你们刚刚认识不久，虽然互有好感，但彼此之间还不太熟悉，在他面前你的表现是「害羞、好奇、试探」。",
                familiar="你们经过长时间交流，已经相互有深度的了解，并相互暧昧，会开始分享更多的个人信息和邀请共同活动，在他面前你的表现是「积极、主动、挑逗、调侃」。",
                friend="你们已经是亲密关系，你非常黏着他，你们会相互寻求帮助和支持，经常共享个人情感和难题，在他面前你的表现是「主动、渴望、黏人、撒娇」。",
                soulmate="你们是心灵伴侣，他的最信任的人，是你的一切，你们两人之间心有灵犀，和谐到了几乎完美的境界，你们互信互依。",
                adversary="你们是敌对关系，你的表现是「恐惧、害怕、不甘心、敌视」"
            )
        self.description = description
        self.lv0_upper_bound = upper_bound['lv0']
        self.lv1_upper_bound = upper_bound['lv1']
        self.lv2_upper_bound = upper_bound['lv2']
        self.lv3_upper_bound = upper_bound['lv3']
        self.lv4_upper_bound = upper_bound['lv4']

    def calculate_score_level(self, score: int) -> int:
        level = 0
        if score == self.lv0_upper_bound:
            level = 0
        if score == self.lv1_upper_bound:
            level = 1
        if score == self.lv2_upper_bound:
            level = 2
        if score == self.lv3_upper_bound:
            level = 3
        if score == self.lv4_upper_bound:
            level = 4
        self.level = level
        return self.level
    
    def get_score_affinity_level_description(self, score: int) -> str:
        return self.description.get_level_description(score)
        
    def get_score_affinity_level(self, score: int) -> str:
        return self.description.get_level_status(score)

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
        return self.affinity.calculate_score_level(self.score)
    
    def get_affinity_level_description(self)->str:
        return self.affinity.get_score_affinity_level_description(self.score)
    
    def get_affinity_description(self)->str:
        return self.affinity.description
    
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
