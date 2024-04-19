import unittest

class TestWebserver(unittest.TestCase):
    def test_modify_user_password(self):
        score = 5
        step = 10
        if step == 0:
            step = 10
        level = score // step
        print('level: ', level)


if __name__ == "__main__":
    unittest.main()