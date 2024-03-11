import unittest
import os
from datetime import datetime
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

from gamenpc.db import database

# 从环境变量中读取数据库配置信息
# 环境变量 MYSQL_DB_CONFIG 数据结构为 “{user}:{password}@{host}”
db_config = os.environ['MYSQL_DB_CONFIG']
db_database = "game"
db_uri = f'mysql+mysqldb://{db_config}/'

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 创建测试数据库引擎和Session
        cls.engine = create_engine(db_uri + db_database)
        database.Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        # 尝试连接到数据库，如果数据库不存在，那么就创建一个新的数据库
        try:
            cls.engine = create_engine(db_uri)
            cls.engine.connect()
        except exc.OperationalError:
            cls.engine = create_engine(db_uri)
            conn = cls.engine.connect()
            conn.execute(f"CREATE DATABASE {db_database}")
            conn.close()

    def test_npc_config(self):
        # 创建新的Session 对象
        session = self.Session()

        # 创建测试NPCConfig对象
        test_npc = database.NPCConfig(
            name='Test NPC',
            short_description='Short Description',
            trait='Trait',
            prompt_description='Prompt Description',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            profile='Profile',
            chat_background='Chat Background',
            affinity_level_description='Affinity Level Description',
            knowledge_id='Knowledge ID'
        )

        # 把测试对象添加到会话中，准备保存到数据库
        session.add(test_npc)
        # 保存对象到数据库
        session.commit()

        # 确认数据已保存
        saved_data = session.query(database.NPCConfig).first()
        self.assertEqual(saved_data.name, 'Test NPC')

        session.close()

    def test_user(self):
        # 创建新的Session 对象
        session = self.Session()

        # 创建测试NPCConfig对象
        test_user = database.User(
            name="玩家1",
            sex="男",
            phone="13645678901",
            money=100,
            create_at=datetime.now()
        )

        # 把测试对象添加到会话中，准备保存到数据库
        session.add(test_user)
        # 保存对象到数据库
        session.commit()

        # 确认数据已保存
        saved_data = session.query(database.User).first()
        self.assertEqual(saved_data.name, '玩家1')

        session.close()

    def test_create_npc_user(self):
        session = self.Session()

        # 创建一个npc_user对象
        new_npc_user = database.NPCUser(
            npc_id=1,
            user_id=1,
            scene='宅在家中',
            score=10,
            phone='1234567890',
            money=100
        )
        session.add(new_npc_user)
        session.commit()

        # 检查数据是否已经正确存入数据库
        npc_user_in_db = session.query(database.NPCUser).one()
        self.assertEqual(npc_user_in_db.id, 1)
        self.assertEqual(npc_user_in_db.scene, '宅在家中')

        session.close()

    @classmethod
    def tearDownClass(cls):
        # 在所有测试运行完毕后，删除测试数据库
        database.Base.metadata.drop_all(cls.engine)


if __name__ == '__main__':
    unittest.main()