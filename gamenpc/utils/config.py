import os
from urllib.parse import quote
from gamenpc.store.mysql_client import MySQLDatabase
from gamenpc.store.redis import RedisDB
from gamenpc.utils.logger import debuglog

class Config:
    def __init__(self, config_file=None):
        if config_file is None:
            mysql_host = os.environ.get('MYSQL_HOST')
            mysql_port = os.environ.get('MYSQL_PORT')
            mysql_user = os.environ.get('MYSQL_USER')
            mysql_password = os.environ.get('MYSQL_PASSWORD')
            mysql_database = os.environ.get('MYSQL_DATABASE')
            redis_host = os.environ.get('REDIS_HOST')
            redis_port = os.environ.get('REDIS_PORT')
            redis_user = os.environ.get('REDIS_USER')
            redis_password = os.environ.get('REDIS_PASSWORD')
            redis_db = os.environ.get('REDIS_DATABASE')
        debuglog.info(f"MySQL:\n host:{mysql_host}; port: {mysql_port}; user: {mysql_user}; passwd: {mysql_password}, database: {mysql_database}")
        self.mysql_client = MySQLDatabase(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password, database=mysql_database)
        self.redis_client = RedisDB(host=redis_host, port=redis_port, user=redis_user, password=redis_password, db=int(redis_db))