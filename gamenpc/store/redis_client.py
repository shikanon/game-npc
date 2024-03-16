import redis
import pickle
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