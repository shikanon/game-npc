from typing import List
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MySQLDatabase:
    def __init__(self, host:str, port:str, user:str, password:str, database:str):
        new_password = quote_plus(password)
        config = f"mysql+pymysql://{user}:{new_password}@{host}:{port}/{database}"
        self.engine = create_engine(config)        
        self.session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_engine(self): 
        return self.engine

    def insert_record(self, record)->any:
        session = self.session()
        session.add(record)
        session.commit()
        session.refresh(record)  # update the record object with new data from database
        return record

    def delete_record_by_id(self, record_class, id):
        session = self.session()
        record = session.query(record_class).filter_by(id=id).first()
        if record:    # 判断是否查找到相应记录
            session.delete(record)
            session.commit()
        else:
            print("没有找到对应id的记录, 无法删除")

    def update_record(self, record)->any:
        session = self.session()
        session.merge(record)
        session.commit()
        return record
    
    # def delete_records(self, record_class, filter_dict):
    #     session = self.session()
    #     records = session.query(record_class).filter_by(**filter_dict)
    #     deleted_records_count = records.delete(synchronize_session=False)
    #     session.commit()
    #     return deleted_records_count

    # def select_records(self, record_class, filter_dict=None)->List:
    #     session = self.session()
    #     if filter_dict == None:
    #         result = session.query(record_class).all()
    #     else:
    #         result = session.query(record_class).filter_by(**filter_dict).all()
    #     return result
    
    def select_records(self, record_class, order_by=None, filter_dict=None, page=1, per_page=10)->List:
        session = self.session()
        query = session.query(record_class)
        if filter_dict is not None:
            query = query.filter_by(**filter_dict)
        if order_by is not None:
            if isinstance(order_by, str):                      # order_by 默认为升序
                query = query.order_by(order_by)
            elif isinstance(order_by, dict):                   # 如果为字典时，key也就是需要排序的字段，value为True则为升序，False则为降序
                for key, value in order_by.items():
                    if value:
                        query = query.order_by(key)
                    else:
                        query = query.order_by(desc(key))
        if page is not None and per_page is not None:         # 加入分页功能
            query = query.limit(per_page).offset((page-1)*per_page)
        results = query.all()
        return results