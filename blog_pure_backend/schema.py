from datetime import datetime
import hashlib
import uuid
from sqlalchemy import and_
import graphene
from graphene.types import Scalar
# noinspection PyPackageRequirements
from graphql.language import ast

from .database import meta, session

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


class EssayFilter(graphene.InputObjectType):
    offset = graphene.Field(graphene.Int, required=True)
    limit = graphene.Field(graphene.Int, required=True)
    tag = graphene.Field(graphene.String)
    year_time = graphene.Field(YearTime)


class Essay(graphene.ObjectType):
    essay_id = graphene.Field(graphene.String)
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
    essays = graphene.Field(graphene.NonNull(graphene.List(graphene.NonNull(Essay))),
                            essay_filter=EssayFilter(required=True))
    tags = graphene.Field(graphene.NonNull(graphene.List(graphene.NonNull(graphene.String))),
                          essay_id=graphene.String())
    about = graphene.Field(About)

    def resolve_essays(self, info, essay_filter):
        offset, limit = essay_filter.offset, essay_filter.limit
        if offset < 0 or offset < 0:
            raise Exception('参数错误')
        essay_table, tags_table = meta.tables['essay'], meta.tables['tags']
        select_essay_stmt = essay_table.select()
        if essay_filter.year_time:
            end_year = datetime(year=essay_filter.year_time.year+1, month=1, day=1)
            select_essay_stmt = select_essay_stmt.where(and_(
                essay_table.c.create_time > essay_filter.year_time, essay_table.c.create_time < end_year
            ))
        if essay_filter.tag:
            select_essay_stmt = select_essay_stmt.where(and_(
                tags_table.c.essay_id == essay_table.c.essay_id, tags_table.c.name == essay_filter.tag
            ))
        essays = [Essay(
            essay_id=row.essay_id,
            title=row.title,
            body=row.content,
            create_time=row.create_time,
            update_time=row.update_time
        ) for row in session.execute(select_essay_stmt.offset(offset).limit(limit))]
        return essays

    def resolve_tags(self, info, essay_id=None):
        tags_table = meta.tables['tags']
        if essay_id:
            where_stmt = and_(tags_table.c.essay_id == essay_id, tags_table.c.is_category == 0)
        else:
            where_stmt = tags_table.c.is_category == 0
        return [r.name for r in session.execute(tags_table.select().where(where_stmt).group_by(tags_table.c.name))]

    def resolve_about(self, info):
        row = session.execute(meta.tables['about'].select()).fetchone()
        return About(name=row.name, age=row.age, sex=row.sex, github=row.github, mail=row.mail)


def verify_password(s):
    p = session.execute(meta.tables['password'].select()).fetchone()
    if p is None:
        return False
    return p.value == hashlib.sha256((salt + s + salt).encode()).hexdigest()


# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal
class CreateEssay(graphene.Mutation):
    class Arguments:
        password = graphene.Argument(graphene.String, required=True)
        title = graphene.Argument(graphene.String, required=True)
        body = graphene.Argument(graphene.String, required=True)

    essay_id = graphene.Field(graphene.String)
    ok = graphene.Field(graphene.Boolean)
    message = graphene.Field(graphene.String)

    def mutate(self, info, password, title, body):
        if not verify_password(password):
            return CreateEssay(essay_id=None, ok=False, message='Incorrect password!')
        essay_id = uuid.uuid1()
        session.execute(
            meta.tables['essay'].insert(),
            {'essay_id': essay_id, 'title': title, 'content': body, 'create_time': datetime.now()}
        )
        session.commit()
        return CreateEssay(essay_id=essay_id, ok=True, message='Success')


# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal
class UpdateEssay(graphene.Mutation):
    class Arguments:
        password = graphene.Argument(graphene.String, required=True)
        essay_id = graphene.Argument(graphene.String, required=True)
        title = graphene.Argument(graphene.String)
        body = graphene.Argument(graphene.String)

    ok = graphene.Field(graphene.Boolean)
    message = graphene.Field(graphene.String)

    def mutate(self, info, password, essay_id, title, body):
        if not verify_password(password):
            return CreateEssay(ok=False, message='Incorrect password!')
        data = dict()
        if title:
            data['title'] = title
        if body:
            data['content'] = body
        if data and essay_id:
            session.execute(meta.tables['essay'].update().where(meta.tables['essay'].c.essay_id == essay_id), data)
            session.commit()
            return UpdateEssay(ok=True, message='Success')
        return UpdateEssay(ok=False, message='Fail')


class Mutation(graphene.ObjectType):
    create_essay = CreateEssay.Field()
    update_essay = UpdateEssay.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
