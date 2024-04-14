import unittest
from gamenpc.tools import generator

class TestGeneratorNpcTrait(unittest.TestCase):
    def test_generator_npc_trait(self):
        name = "爱莉"
        sex = "女"
        short_description = """爱莉，从小跟着哥哥一起长大，天真和顽皮的撒娇，特别依赖哥哥，是个哥哥控"""
        
        result = generator.generator_npc_trait(name, sex, short_description)
        
        self.assertIsInstance(result, str)
        print(result)

if __name__ == '__main__':
    unittest.main()