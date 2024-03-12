import redis

class RedisList:
    def __init__(self, host='localhost', port=6379, user="root", password='', db=0):
        self.redis = redis.Redis(host=host, port=port,username=user, password=password, db=db)

    def push(self, name, value):
        return self.redis.lpush(name, value)

    def pop(self, name):
        return self.redis.lpop(name)

    def get_all(self, name):
        return self.redis.lrange(name, 0, -1)
    
    def delete(self, name):
        return self.redis.delete(name)