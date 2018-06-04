import graphene
from .database import meta, session


class Comment(graphene.ObjectType):
    name = graphene.Field(graphene.String)
    mail = graphene.Field(graphene.String)
    content = graphene.Field(graphene.String)
    create_time = graphene.Field(graphene.types.datetime.DateTime)


class Essay(graphene.ObjectType):
    essay_id = graphene.Field(graphene.Int)
    title = graphene.Field(graphene.String)
    labels = graphene.List(graphene.NonNull(graphene.String))
    body = graphene.Field(graphene.String)
    comments = graphene.List(graphene.NonNull(Comment))
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
    essays = graphene.Field(graphene.List(graphene.NonNull(Essay)), first=graphene.Int(), after=graphene.Int())
    labels = graphene.Field(graphene.List(graphene.NonNull(graphene.String)))
    about = graphene.Field(About)

    def resolve_essays(self, info, first, after):
        essay_table = meta.tables['essay']
        essays = [Essay(
            essay_id=row.id,
            title=row.title,
            labels=['标签1', '标签2'],
            body=row.content,
            comments=[Comment(name='', mail='', content='', create_time='')],
            create_time=row.create_time,
            update_time=row.update_time
        ) for row in session.execute(essay_table.select().where(essay_table.c.id > after).limit(first))]
        return essays

    def resolve_about(self, info):
        row = session.execute(meta.tables['about'].select()).fetchone()
        return About(name=row['name'], age=row['age'], sex=row['sex'], github=row['github'], mail=row['mail'])


schema = graphene.Schema(query=Query)
