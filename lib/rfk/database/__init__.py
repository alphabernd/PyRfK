from sqlalchemy import create_engine
from sqlalchemy.orm import relationship,sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None
session = None


def init_db(db_uri):
    global session, engine
    engine = create_engine(db_uri)
    session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
    Base.query = session.query_property()
    import base
    import show
    Base.metadata.create_all(bind=engine)
    Base.query = session.query_property()
    