from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
engine = create_engine('mysql+pymysql://root:111111@localhost:3306/dist_weibo?charset=utf8')
DBSession = sessionmaker(bind=engine)
db_session = DBSession()



