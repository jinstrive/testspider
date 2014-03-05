import redis

class RedisOper(object):
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost',port=6379,db=0)
        self._redis = redis.Redis(connection_pool=pool)
    
    def sadd(self,key,value):
        return self._redis.sadd(key,value)
    
    def scard(self,key):
        return self._redis.scard(key)
    
    
if __name__ == "__main__":
    myredis = RedisOper()
    key = "set_test"
    print myredis.sadd(key, 1)
    print myredis.sadd(key, 1)
        