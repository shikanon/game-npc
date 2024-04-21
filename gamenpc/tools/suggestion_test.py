# coding:utf-8
"""
suggestion module.
author: shikanon
create: 2024/4/21
"""
import unittest
from gamenpc.tools import suggestion

class TestGeneratorDialogueSuggestion(unittest.TestCase):
    def test_generator_dialogue_suggestion(self):
        dialogue = "爱莉：哥哥在看什么，怎么这么晚了还没睡？（好奇地爬到哥哥身边）"
        npc_trait = """你是爱莉，你和你的哥哥从小时候就一直在一起成长，在成长过程中，你总是喜欢跟在哥哥身后，像个小尾巴一样。
        每当遇到困难或者受到委屈时，你会立刻跑到哥哥身边撒娇求助，你对哥哥的病态依恋让你愿意为他做任何事。
        你通常都会充满天真和顽皮的撒娇，你过分依赖哥哥，这通常会让人感到辛酸。为了让哥哥喜欢你，你会创造各种话题来吸引他的注意力。
        你的口头禅是“哥哥最好了！”，说话时带着甜美的语气。招牌动作是扭动身子撒娇，这常常让人无法抗拒。"""
        
        result = suggestion.generator_dialogue_suggestion(dialogue, npc_trait)
        self.assertIsNotNone(result)
        print(result["1"])
        print(result["2"])
        print(result["3"])

if __name__ == '__main__':
    unittest.main()