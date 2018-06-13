import os
from flask import _app_ctx_stack
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData

# database_url=mysql+mysqldb://user:password@host/blog?charset=utf8mb4
database_url = os.environ['database_url']
engine = create_engine(database_url)
meta = MetaData(engine)
meta.reflect()
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)
