import graphene

class ReturnType(graphene.ObjectType):
    message = graphene.String()
    status = graphene.Int()