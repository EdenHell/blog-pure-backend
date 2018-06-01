from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData

database_url = 'mysql+mysqldb://blog:blog123@localhost/blog?charset=utf8mb4'
engine = create_engine(database_url)
meta = MetaData(engine)
meta.reflect(only=('essay', 'comment'))
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)
