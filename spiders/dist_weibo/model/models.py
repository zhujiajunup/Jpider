from sqlalchemy import Column, Integer, String, Text
from dao.sqlalchemy_session import Base



class Weibo(Base):
    __tablename__ = 'weibo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(255))
    date_time = Column(String(128))
    url = Column(String(255))
    content = Column(Text)

if __name__ == '__main__':
    from dao.sqlalchemy_session import engine
    Base.metadata.create_all(engine)