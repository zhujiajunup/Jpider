from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import traceback
Base = declarative_base()
engine = create_engine('mysql+pymysql://root:111111@localhost:3306/dist_weibo?charset=utf8')

class SqlSession(object):


    DBSession = sessionmaker(bind=engine)

    @classmethod
    def insert(cls, obj):
        session = cls.DBSession()
        try:
            session.add(obj)
            session.commit()
        except:
            print(traceback.format_exc())
            session.rollback()
        finally:
            session.close()
