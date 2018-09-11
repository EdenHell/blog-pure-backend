# noinspection PyProtectedMember
from flask import _app_ctx_stack
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy import BigInteger, CHAR, Column, DateTime, Integer, SmallInteger, String, Table, Text
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData(engine)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)


Table(
    'about', metadata,
    Column('id', BigInteger),
    Column('name', String(16)),
    Column('mail', String(128)),
    Column('github', String(128)),
    Column('age', Integer),
    Column('sex', CHAR(2)),
    Column('create_time', DateTime),
    Column('update_time', DateTime)
)


Table(
    'password', metadata,
    Column('value', String(128))
)


Table(
    'posts', metadata,
    Column('id', BigInteger),
    Column('post_id', String(128)),
    Column('title', String(256)),
    Column('body', Text),
    Column('create_time', DateTime),
    Column('update_time', DateTime)
)


Table(
    'tags', metadata,
    Column('id', BigInteger),
    Column('essay_id', String(128)),
    Column('name', String(128)),
    Column('is_category', SmallInteger)
)
