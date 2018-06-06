from datetime import datetime
from sqlalchemy import and_
import graphene
from graphene.types import Scalar
# noinspection PyPackageRequirements
from graphql.language import ast

from .database import meta, session


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
    first = graphene.Field(graphene.Int, required=True)
    after = graphene.Field(graphene.Int, default_value=0)
    tag = graphene.Field(graphene.String)
    year_time = graphene.Field(YearTime)


class Comment(graphene.ObjectType):
    name = graphene.Field(graphene.String)
    mail = graphene.Field(graphene.String)
    content = graphene.Field(graphene.String)
    create_time = graphene.Field(graphene.types.datetime.DateTime)


class Essay(graphene.ObjectType):
    essay_id = graphene.Field(graphene.Int)
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
                          essay_id=graphene.Int())
    comments = graphene.Field(graphene.NonNull(graphene.List(graphene.NonNull(Comment))),
                              essay_id=graphene.Int(required=True))
    about = graphene.Field(About)

    def resolve_essays(self, info, essay_filter):
        first, after = essay_filter.first, essay_filter.after
        if first < 0 or after < 0:
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
                tags_table.c.essay_id == essay_table.c.id, tags_table.c.name == essay_filter.tag
            ))
        essays = [Essay(
            essay_id=row.id,
            title=row.title,
            body=row.content,
            create_time=row.create_time,
            update_time=row.update_time
        ) for row in session.execute(select_essay_stmt.where(essay_table.c.id > after).limit(first))]
        return essays

    def resolve_tags(self, info, essay_id=None):
        tags_table = meta.tables['tags']
        if essay_id:
            where_stmt = and_(tags_table.c.essay_id == essay_id, tags_table.c.is_category == 0)
        else:
            where_stmt = tags_table.c.is_category == 0
        return [r.name for r in session.execute(tags_table.select().where(where_stmt).group_by(tags_table.c.name))]

    def resolve_comments(self, info, essay_id):
        comment_table = meta.tables['comment']
        return [Comment(
            name=r.name, mail=r.mail, content=r.content, create_time=r.create_time
        ) for r in session.execute(comment_table.select().where(comment_table.c.essay_id == essay_id))]

    def resolve_about(self, info):
        row = session.execute(meta.tables['about'].select()).fetchone()
        return About(name=row.name, age=row.age, sex=row.sex, github=row.github, mail=row.mail)


schema = graphene.Schema(query=Query)
