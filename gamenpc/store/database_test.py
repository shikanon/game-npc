import unittest
from datetime import datetime
from gamenpc.store import database

class TestNPCModel(unittest.TestCase):
    def setUp(self):
        self.session = database.DBSession()
        
    def tearDown(self):
        self.session.close()

    def test_add_npc(self):
        npc = database.NPC(
            name="Test NPC", 
            short_description="This is a Test NPC", 
            trait='Trait',
            prompt_description='Prompt Description',
            created_at=datetime.now(),
            updated_at=datetime.now(),
            profile='Profile',
            chat_background='Chat Background',
            affinity_level_description='Affinity Level Description',
            knowledge_id='Knowledge ID'
        )
        npc.add()
        self.assertIsNotNone(self.session.query(database.NPC).filter(database.NPC.name=="Test NPC").first())

    def test_update_npc(self):
        npc = self.session.query(database.NPC).filter(database.NPC.name=="Test NPC").first()
        npc.short_description = "Updated description"
        npc.update()
        self.assertEqual(self.session.query(database.NPC).filter(database.NPC.name=="Test NPC").first().short_description, "Updated description")

    def test_delete_npc(self):
        npc_id = self.session.query(database.NPC).filter(database.NPC.name=="Test NPC").first().id
        database.NPC.delete(npc_id)
        self.assertIsNone(self.session.query(database.NPC).filter(database.NPC.name=="Test NPC").first())

if __name__ == "__main__":
    unittest.main()