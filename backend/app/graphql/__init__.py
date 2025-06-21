import graphene
from .users import GetUsers, AddUser

class Query(GetUsers, graphene.ObjectType):
    pass

class Mutation(graphene.ObjectType):
    add_user = AddUser.Field()

schema = graphene.Schema(
                            query=Query,
                            mutation=Mutation
                        )
