import graphene
from .users import GetUsers
from .posts import GetPosts, AddPost

class Query(GetUsers, GetPosts, graphene.ObjectType):
    pass

class Mutation(graphene.ObjectType):
    add_post = AddPost.Field()

schema = graphene.Schema(
                            query=Query,
                            mutation=Mutation
                        )
