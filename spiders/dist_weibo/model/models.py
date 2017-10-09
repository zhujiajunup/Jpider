from sqlalchemy import Column, Integer, String, Text
from dao.sqlalchemy_session import Base



class Weibo(Base):
    __tablename__ = 'weibo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(255))
    date_time = Column(String(128))
    url = Column(String(255))
    content = Column(Text)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128))
    nickname = Column(String(255))
    realname = Column(String(255))
    location = Column(String(255))
    gender = Column(String(4))
    sexual_ori = Column(String(128))
    emotion_state = Column(String(64))
    birthday = Column(String(16))
    blood_type = Column(String(2))
    blog = Column(String(255))
    domain_name = Column(String(255))
    intro = Column(Text)
    register_time = Column(String(16))
    email = Column(String(64))
    company = Column(String(128))
    college = Column(String(255))
    high_school = Column(String(255))
    mid_school = Column(String(255))
    tags = Column(String(255))

class Relationship(Base):
    __tablename__ = 'relationship'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128))
    fan_id = Column(String(128))


class CrawlInfo(Base):
    __tablename__ = 'crawl_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128))
    last_crawl_date = Column(String(20))

if __name__ == '__main__':
    from dao.sqlalchemy_session import engine
    Base.metadata.create_all(engine)