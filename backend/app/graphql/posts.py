from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User, Post, db
from .return_types import ReturnType

class PostType(SQLAlchemyObjectType):
    class Meta:
        model = Post

class GetPosts(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    posts_by_user = graphene.List(PostType, user_id=graphene.Int())

    def resolve_all_posts(self, info):
        return Post.query.all()
    
    def resolve_posts_by_user(self, info, user_id):
        return Post.query.filter(Post.user_id == user_id).all()
    
class AddPost(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    Output = ReturnType

    def mutate(root, info, user_id, title, content):
        user = User.query.get(user_id)
        if user:
            try:
                db.session.add(Post(title=title, content=content, user_id=user.id))
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                print(err)
                return ReturnType(message="Failure", status=500)
            else:
                return ReturnType(message="Success", status=200)
        return ReturnType(message="User not found", status=404)
