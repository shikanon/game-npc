import uuid
import os

from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, text
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Tuple
from datetime import datetime
from dataclasses import dataclass

from gamenpc.store.mysql_client import MySQLDatabase, Base
from datetime import datetime
from jwt import JWT
from datetime import datetime

@dataclass
class Plot(Base):
    # 表的名字
    __tablename__ = 'plot'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String(255))
    npc_id = Column(String(255))
    cover_url = Column(String(255))
    bg_url = Column(String(255))
    status = Column(Integer)
    description = Column(Text)
    content = Column(Text)
    updated_at = Column(DateTime, default=datetime.now())
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, id=None, npc_id=None, name=None, cover_url=None, bg_url=None, status=0, description=None, content=None):
        self.id = id
        self.npc_id = npc_id
        self.name = name
        self.cover_url = cover_url
        self.bg_url = bg_url
        self.status = status
        self.description = description
        self.content = content
    
    def to_dict(self):
        return {
            'id': self.id,
            'npc_id': self.npc_id,
            'name': self.name,
            'cover_url': self.cover_url,
            'bg_url': self.bg_url,
            'status': self.status,
            'description': self.description,
            'content': self.content,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
    
class PlotManager:
    def __init__(self, mysql_client: MySQLDatabase):
        self.mysql_client = mysql_client

    def get_plots(self, order_by=None, filter_dict=None, page=1, limit=10) -> Tuple[List[Plot], int]:
        plots, total = self.mysql_client.select_records(record_class=Plot, order_by=order_by, filter_dict=filter_dict, page=page, limit=limit)
        return plots, total
    
    def get_plot(self, filter_dict) -> Plot:
        plot = self.mysql_client.select_record(record_class=Plot, filter_dict=filter_dict)
        if plot == None:
            return None
        return plot
    
    def set_plot(self, id="", npc_id="", name="", cover_url="", bg_url="", status=-1, description="", content="") -> Plot:
        # 创建新剧本
        plot = Plot(name=name, npc_id=npc_id, bg_url=bg_url, cover_url=cover_url, status=status, description=description, content=content)
        if id != "":
            plot = Plot(id=id, npc_id=npc_id, name=name, bg_url=bg_url, cover_url=cover_url, status=status, description=description, content=content)
        plot = self.mysql_client.insert_record(plot)
        return plot
    
    def update_plot(self, id="", npc_id="", name="", cover_url="", bg_url="", status=-1, description="", content="") -> Plot:
        filter_dict = {'id': id}
        plot = self.mysql_client.select_record(record_class=Plot, filter_dict=filter_dict)
        if plot == None:
            return None
        if name != "":
            plot.name = name
        if cover_url != "":  
            plot.cover_url = cover_url
        if bg_url != "":  
            plot.bg_url = bg_url
        if status != -1: 
            plot.status = status
        if npc_id != "":
            plot.npc_id = npc_id
        if content != "": 
            plot.content = content
        if description != "": 
            plot.description = description
        plot.updated_at = datetime.now()
        plot = self.mysql_client.update_record(plot)
        return plot
    
    def remove_plot(self, plot_id: str):
        self.mysql_client.delete_record_by_id(record_class=Plot, id=plot_id)