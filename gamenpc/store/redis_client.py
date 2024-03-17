import redis
import pickle
import os
# from urllib.parse import quote_plus

class RedisList:
    def __init__(self, host='localhost', port=6379, user="root", password='', db=0):
        print('host: ', host)
        print('port: ', port)
        print('user: ', user)
        print('password: ', password)
        print('db: ', db)
        self.redis_client = redis.Redis(host=host, port=port, username=user, password=password, db=db)

    def push(self, name, value):
        valuetes = pickle.dumps(value)
        print('name: ', str(name))
        print('valuetes: ', str(valuetes))
        return self.redis_client.lpush(name, valuetes)

    def pop(self, name):
        return self.redis_client.lpop(name)

    def get_all(self, name):
        return self.redis_client.lrange(name, 0, -1)
    
    def delete(self, name):
        return self.redis_client.delete(name)
    
redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT')
redis_user = os.environ.get('REDIS_USER')
redis_password = os.environ.get('REDIS_PASSWORD')
redis_db = os.environ.get('REDIS_DATABASE')
redis_client = RedisList(host=redis_host, port=redis_port, user=redis_user, password=redis_password, db=int(redis_db))
user_id = "42ae0aeb-96c8-4569-8a61-9063ddcfa699"
npc_id = "ecedb3a2-007e-4ca8-bd65-6f13bb9640fd"
list_name = f'dialogue_{npc_id}_{user_id}'
dialogues = redis_client.get_all(list_name)
print('dialogues:', dialogues)