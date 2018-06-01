import graphene
from .database import meta, session
# noinspection PyMethodMayBeStatic
# noinspection PyUnusedLocal


class Query(graphene.ObjectType):
    essays = graphene.Field(graphene.String)

    def resolve_essays(self, info, _id):
        return [Essay(**row) for row in session.execute(meta.tables['essay'].select())]


class Essay(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
