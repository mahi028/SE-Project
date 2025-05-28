import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..modals import User, Post
    
class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User

class PostType(SQLAlchemyObjectType):
    class Meta:
        model = Post

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_posts = graphene.List(PostType)
    
    user = graphene.Field(UserType, id=graphene.Int(), username=graphene.String())
    posts_by_user = graphene.List(PostType, user_id=graphene.Int())
    
    def resolve_all_users(self, info):
        return User.query.all()
    
    def resolve_all_posts(self, info):
        return Post.query.all()
    
    def resolve_user(self, info, id=None, username=None):
        query = User.query
        if id:
            return query.filter(User.id == id).first()
        if username:
            return query.filter(User.username == username).first()
        return None
    
    def resolve_posts_by_user(self, info, user_id):
        return Post.query.filter(Post.user_id == user_id).all()

schema = graphene.Schema(query=Query)
