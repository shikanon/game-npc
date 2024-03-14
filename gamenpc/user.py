from sqlalchemy import Column, String, Integer, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from gamenpc.npc import NPCUser, NPCManager
from gamenpc.store.mysql import MySQLDatabase, Base
from typing import List
import uuid
from datetime import datetime
from dataclasses import dataclass


class UserManager:
    def __init__(self, client: MySQLDatabase, npc_manager: NPCManager):
        self.client = client
        self.npc_manager = npc_manager

    def get_users(self, order_by=None, filter_dict=None, page=1, limit=10) -> List[User]:
        users = self.client.select_records(User, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return users
    
    def get_user(self, filter_dict=None) -> User:
        users = self.client.select_records(User, filter_dict=filter_dict)
        if len(users) == 0:
            return None
        print(users)
        user = users[0]
        return user
    
    def set_user(self, name, sex, phone, money, password) -> User:
        filter_dict = {'phone': phone}
        print('phone: ', phone)
        users = self.client.select_records(User, filter_dict=filter_dict)
        print('users len: ', len(users))
        if len(users) == 1:
            return None
        else:
            # 创建新用户
            user = User(name=name, sex=sex, phone=phone, money=money, password=password)
            user = self.client.insert_record(user)
            return user
           
    
    def update_user(self, id, name, sex, phone, money, password) -> User:
        # self._instances[user.id] = user
        user.id = id
        user.name = name
        user.sex = sex
        user.phone = phone
        user.money = money
        user.password = password
        user = self.client.update_record(user)
        return user
    
    def remove_user(self, user_id: str):
        self.client.delete_record_by_id(User, user_id)
        