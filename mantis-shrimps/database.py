# noinspection PyProtectedMember
from flask import _app_ctx_stack
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData(engine)
metadata.reflect()
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)
