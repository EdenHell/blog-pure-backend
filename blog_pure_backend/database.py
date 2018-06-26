import os
# noinspection PyProtectedMember
from flask import _app_ctx_stack
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData

# database_url=postgresql+pg8000://user:password@host/blog
database_url = os.environ['database_url']
engine = create_engine(database_url)
meta = MetaData(engine)
meta.reflect()
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)
