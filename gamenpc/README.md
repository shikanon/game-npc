# 接口文档


# 数据库表结构设计

## 关系数据库

### NPC表

|   列名   |   数据类型         |  主键  | 默认值 | 唯一 | 外键 | 关系 |     描述     |
|---------|-----------------|--------|--------|-----|-----|----|--------------|
| id    | String(255)   |  是    |uuid.uuid4| 是  |    |    | NPC ID，uuid   |
| name  | String(64)    |  否    | None   | 否  |    |    | NPC名称       |
| short_description | String(255)| 否 | None | 否 |    |    | 短描述，主要用于前端展示 |
| trait   | Text           |  否    | None   | 否  |    |    | NPC特征，提示词内容 |
| prompt_description | Text  |  否    | None   | 否  |    |    | 提示词描述，存储完整提示词模板 |
| profile  | Text           |  否    | None   | 否  |    |    | 头像图片路径 |
| chat_background| Text   |  否    | None   | 否  |    |    | 聊天背景图片路径 |
| affinity_level_description| Text |  否 | None| 否 |  |  | 亲密度等级行为倾向描述 |
| knowledge_id  | String(255)  |  否 | None | 否  |    |    | 知识库的 index id |
| updated_at | DateTime  |  否    |datetime.now| 否 |    |   | 更新时间 |
| created_at | DateTime  |  否    |datetime.now| 否 |    |   | 创建时间 |

ORM设计：
```python
class NPC(Base):
    # 表的名字
    __tablename__ = 'npc'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True) # NPC ID，uuid
    name = Column(String(64)) # NPC名称
    short_description = Column(String(255)) # 短描述，主要用于前端展示
    trait = Column(Text) #  NPC特征，提示词内容
    prompt_description = Column(Text) # 提示词描述，存储完整提示词模板
    profile = Column(Text) # 头像图片路径
    chat_background = Column(Text) # 聊天背景图片路径
    affinity_level_description = Column(Text) # 亲密度等级行为倾向描述
    knowledge_id = Column(String(255)) # 知识库的 index id
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now()) # 创建时间
    created_at = Column(DateTime, default=datetime.now())
```

### User表

|   列名   |   数据类型                  |  主键  | 默认值  | 唯一 | 外键 | 关系 |     描述     |
|---------|----------------------|--------|--------|------|----|----|-----------|
| id      | String(255)          |  是    |uuid.uuid4| 是  |    |    | 用户ID，自增id |
| name    | String(64)           |  否    | None   | 否   |    |    | 用户名称  |
| sex     | Enum("男", "女", "未知") |  否    | None   | 否   |    |    | 性别：男、女、未知 |
| phone   | String(11)           |  否    | None   | 否   |    |    | 手机号   |
| money   | Integer              |  否    | None   | 否   |    |    | 用户虚拟积分    |
| password| String(11)           |  否    | None   | 否   |    |    | 用户密码  |
| created_at | DateTime          |  否    | datetime.now| 否 |  |  | 创建时间  |

ORM设计：
```python
class User(Base):
    # 表的名字
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True) # 用户ID，自增id
    name = Column(String(64)) # 用户名称 
    sex = Column(Enum("男", "女", "未知")) # 性别：男、女、未知
    phone = Column(String(11)) # 手机号
    money = Column(Integer) # 用户虚拟积分
    password = Column(String(11)) # 用户密码
    created_at = Column(DateTime, default=datetime.now()) # 创建时间
```

### Scene表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|-----|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |     |
| scene       | Text       | 否   | None   | 否  |     |    | 场景内容 |
| theater     | Text       | 否   | None   | 否  |     |    | 剧场名称 |
| theater_event | Text       | 否   | None   | 否  |     |    | 剧场事件 |
| roles       | String(255)| 否   | None   | 否  |     |    | 角色列表 |
| score       | String(255)| 否   | None   | 否  |     |    | 评分   |
| created_at  | DateTime   | 否   | datetime.now | 否 | |  | 创建时间 |

ORM设计：
```python
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
```

### NPC_User管理表

|      列名          |    数据类型    |  主键  | 默认值  | 唯一 |         外键          |  关系  |           描述           |
|-------------------|---------------|--------|--------|------|-----------------------|-------|-------------------------|
|       id           |  String(255)  |  是    |uuid.uuid4| 是  |                           |        |                          |
|      npc_id        |  String(255)  |  否    |  None   | 否   | ForeignKey('npc.id')  | NPC   | npc配置对象，外键      |
|     user_id        |  String(255)  |  否    |  None   | 否   | ForeignKey('user.id') | User  | 用户对象，外键         |
|      scene         |  String(255)  |  否    |  None   | 否   |                           |         | 场景描述                  |
|      score         |  Integer      |  否    |  None   | 否   |                           |         | 好感分数                 |
| affinity_level     |  Integer      |  否    |  None   | 否   |                           |         | 亲密度等级             |
|   created_at       |    DateTime   |  否    | datetime.now| 否 |                           |         | 创建时间                 |

ORM设计：
```python
class NPCUser(Base):
        # 表的名字
    __tablename__ = 'npc_user'
    __table_args__ = {'extend_existing': True}

    # 表的结构
    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
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
```

### Event表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|------|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |  ID |
| npc_id      | String(255)| 否   | None | 否  | 是   | NPC | NPC对象，外键 |
| npc         | relationship | 否 | None | 否  |     |    | 关联NPC对象 |
| theater     | String(255)| 否   | None | 否  |     |    | 剧情章节 |
| theater_event | String(255)| 否 | None | 否  |     |    | 剧情的事件（JSON） |
| created_at  | DateTime   | 否   | datetime.now | 否 |     |    | 创建时间 |

ORM设计：
```python
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
```

### UserOpinion表

| 列名          | 数据类型     | 主键 | 默认值 | 唯一 | 外键 | 关系 | 描述 |
|-------------|------------|-----|--------|-----|-----|----|------|
| id          | String(255)| 是   | uuid.uuid4 | 是  |     |    |  ID |
| labels      | String(255)| 否   | None | 否  |     |    | 意见标签（多标签通过逗号隔开） |
| name        | String(255)| 否   | None | 否  |     |    | 用户名称 |
| content     | Text       | 否   | None | 否  |     |    | 用户意见 |
| created_at  | DateTime   | 否   | datetime.now | 否 |     |    | 创建时间 |

ORM设计：
```python
class UserOpinion(Base):
    __tablename__ = 'user_opinion'
    __table_args__ = {'extend_existing': True}

    id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    labels = Column(String(255))  # 意见标签（多标签通过逗号隔开）
    name = Column(String(255))  # 用户名称
    content = Column(Text)  # 用户意见
    created_at = Column(DateTime, default=datetime.now())  # 创建时间

```

## 缓存数据库redis