import redis
import pickle
from gamenpc.utils.logger import debuglog

# debuglog = DebugLogger("redis")

class RedisList:
    def __init__(self, host='localhost', port=6379, user="root", password='', db=0):
        debuglog.info(f'redis init: host = {host}, port = {port}, user = {user}, password = {password}, db = {db}')
        self.redis_client = redis.Redis(host=host, port=port, username=user, password=password, db=db)

    def push(self, name, value):
        valuetes = pickle.dumps(value)
        return self.redis_client.lpush(name, valuetes)

    def pop(self, name):
        return self.redis_client.lpop(name)

    def get_all(self, name):
        return self.redis_client.lrange(name, 0, -1)
    
    def delete(self, name):
        return self.redis_client.delete(name)
    