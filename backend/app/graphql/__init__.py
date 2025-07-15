import graphene
from .users import GetUsers, AddUser
from .auth import GetToken, Register

class Query(GetUsers, GetToken, graphene.ObjectType):
    pass

class Mutation(graphene.ObjectType):
    add_user = AddUser.Field()
    register_user = Register.Field()

schema = graphene.Schema(
                            query=Query,
                            mutation=Mutation
                        )
