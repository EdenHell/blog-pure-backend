from datetime import datetime
import hashlib
import uuid
from sqlalchemy import select
from sqlalchemy import and_
import graphene
from graphene.types import Scalar
# noinspection PyPackageRequirements
from graphql.language import ast

from .database import metadata, session

salt = 'sc&#of78'


class YearTime(Scalar):
    """年份"""

    @staticmethod
    def serialize(y):
        return y.strftime('%Y')

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.strptime(node.value, "%Y")

    @staticmethod
    def parse_value(value):
        return datetime.strptime(value, "%Y")


class AuthResult(graphene.Enum):
    SUCCESS = True
    FAILURE = False


class PostFilter(graphene.InputObjectType):
    offset = graphene.Field(graphene.Int, required=True)
    limit = graphene.Field(graphene.Int, required=True)
    tag = graphene.Field(graphene.String)
    year_time = graphene.Field(YearTime)


class Post(graphene.ObjectType):
    post_id = graphene.Field(graphene.String)
    title = graphene.Field(graphene.String)
    body = graphene.Field(graphene.String)
    create_time = graphene.Field(graphene.types.datetime.DateTime)
    update_time = graphene.Field(graphene.types.datetime.DateTime)


class About(graphene.ObjectType):
    name = graphene.Field(graphene.String)
    age = graphene.Field(graphene.Int)
    sex = graphene.Field(graphene.String)
    github = graphene.Field(graphene.String)
    mail = graphene.Field(graphene.String)


# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal
class Query(graphene.ObjectType):
    posts = graphene.Field(graphene.NonNull(graphene.List(graphene.NonNull(Post))),
                           post_filter=PostFilter(required=True))
    tags = graphene.Field(graphene.NonNull(graphene.List(graphene.NonNull(graphene.String))),
                          post_id=graphene.String())
    about = graphene.Field(About)
    admin_auth = graphene.Field(graphene.NonNull(AuthResult), password=graphene.String(required=True))

    def resolve_posts(self, info, post_filter):
        offset, limit = post_filter.offset, post_filter.limit
        if offset < 0 or offset < 0:
            raise Exception('参数错误')
        post_table, tags_table = metadata.tables['posts'], metadata.tables['tags']
        select_post_stmt = post_table.select()
        if post_filter.year_time:
            end_year = datetime(year=post_filter.year_time.year+1, month=1, day=1)
            select_post_stmt = select_post_stmt.where(and_(
                post_table.c.create_time > post_filter.year_time, post_table.c.create_time < end_year
            ))
        if post_filter.tag:
            select_post_stmt = select_post_stmt.where(and_(
                tags_table.c.post_id == post_table.c.post_id, tags_table.c.name == post_filter.tag
            ))
        posts = [Post(
            post_id=row.post_id,
            title=row.title,
            body=row.body,
            create_time=row.create_time,
            update_time=row.update_time
        ) for row in session.execute(select_post_stmt.offset(offset).limit(limit))]
        return posts

    def resolve_tags(self, info, post_id=None):
        tags_table = metadata.tables['tags']
        if post_id:
            where_stmt = and_(tags_table.c.post_id == post_id, tags_table.c.is_category == 0)
        else:
            where_stmt = tags_table.c.is_category == 0
        stmt = select([tags_table.c.name]).where(where_stmt).group_by(tags_table.c.name)
        return [r.name for r in session.execute(stmt)]

    def resolve_about(self, info):
        row = session.execute(metadata.tables['about'].select()).fetchone()
        return About(name=row.name, age=row.age, sex=row.sex, github=row.github, mail=row.mail)

    def resolve_admin_auth(self, info, password):
        return verify_password(password)


def verify_password(s):
    p = session.execute(metadata.tables['password'].select()).fetchone()
    if p is None:
        return False
    return p.value == hashlib.sha256((salt + s + salt).encode()).hexdigest()


# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal
class CreatePost(graphene.Mutation):
    class Arguments:
        password = graphene.Argument(graphene.String, required=True)
        title = graphene.Argument(graphene.String, required=True)
        body = graphene.Argument(graphene.String, required=True)

    post_id = graphene.Field(graphene.String)
    ok = graphene.Field(graphene.Boolean)
    message = graphene.Field(graphene.String)

    def mutate(self, info, password, title, body):
        if not verify_password(password):
            return CreatePost(post_id=None, ok=False, message='Incorrect password!')
        post_id = uuid.uuid1()
        session.execute(
            metadata.tables['posts'].insert(),
            {'post_id': post_id, 'title': title, 'body': body, 'create_time': datetime.now()}
        )
        session.commit()
        return CreatePost(post_id=post_id, ok=True, message='Success')


# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal
class UpdatePost(graphene.Mutation):
    class Arguments:
        password = graphene.Argument(graphene.String, required=True)
        post_id = graphene.Argument(graphene.String, required=True)
        title = graphene.Argument(graphene.String)
        body = graphene.Argument(graphene.String)

    ok = graphene.Field(graphene.Boolean)
    message = graphene.Field(graphene.String)

    def mutate(self, info, password, post_id, title=None, body=None):
        if not verify_password(password):
            return CreatePost(ok=False, message='Incorrect password!')
        data = dict()
        if title:
            data['title'] = title
        if body:
            data['body'] = body
        if not (data and post_id):
            return UpdatePost(ok=False, message='Fail')
        data['update_time'] = datetime.now()
        session.execute(metadata.tables['posts'].update().where(metadata.tables['posts'].c.post_id == post_id), data)
        session.commit()
        return UpdatePost(ok=True, message='Success')


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
