import pymysql

class MySQLDatabase:
    def __init__(self, host:str, port:int, user:str, password:str, database:str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            port = self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def insert_record(self, table, data):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.execute_query(sql, tuple(data.values()))
        self.connection.commit()
        return cursor.rowcount

    def select_records(self, table, condition=None):
        sql = f"SELECT * FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        cursor = self.execute_query(sql)
        return cursor.fetchall()

    def update_record(self, table, data, condition):
        placeholders = ', '.join([f"{key} = %s" for key in data])
        sql = f"UPDATE {table} SET {placeholders} WHERE {condition}"
        cursor = self.execute_query(sql, tuple(data.values()))
        self.connection.commit()
        return cursor.rowcount

    def delete_record(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        cursor = self.execute_query(sql)
        self.connection.commit()
        return cursor.rowcount
    
    def create_table(self, create_table_sql):
        # 创建游标对象
        cursor = self.connection.cursor()
        # 执行 SQL 语句
        cursor.execute(create_table_sql)
        # 提交事务
        self.connection.commit()
        # 关闭游标和连接
        cursor.close()
