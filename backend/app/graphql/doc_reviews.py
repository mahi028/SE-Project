from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import DocReviews, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb

class DocReviewType(SQLAlchemyObjectType):
    class Meta:
        model = DocReviews

# Query for getting reviews by doctor ID, average rating, and review count
class DocReviewsQuery(graphene.ObjectType):
    get_doc_reviews = graphene.List(DocReviewType, doc_id=graphene.Int(required=True))
    get_average_rating = graphene.Float(doc_id=graphene.Int(required=True))
    get_review_count = graphene.Int(doc_id=graphene.Int(required=True))
    get_all_reviews = graphene.List(DocReviewType)

    def resolve_get_doc_reviews(self, info, doc_id):
        return DocReviews.query.filter_by(doc_id=doc_id).all()

    def resolve_get_average_rating(self, info, doc_id):
        reviews = DocReviews.query.filter_by(doc_id=doc_id).all()
        if not reviews:
            return 0.0
        total = sum([r.rating for r in reviews if r.rating is not None])
        return round(total / len(reviews), 1)

    def resolve_get_review_count(self, info, doc_id):
        return DocReviews.query.filter_by(doc_id=doc_id).count()

    def resolve_get_all_reviews(self, info):
        return DocReviews.query.all()

# Mutation for adding a doctor review
class AddDocReview(graphene.Mutation):
    class Arguments:
        doc_id = graphene.Int(required=True)
        sen_id = graphene.Int(required=True)
        rating = graphene.Int(required=True)
        review = graphene.String()

    Output = ReturnType

    def mutate(self, info, doc_id, sen_id, rating, review=None):
        doc_review = DocReviews(
            doc_id=doc_id,
            sen_id=sen_id,
            rating=rating,
            review=review
        )
        adddb(doc_review)
        try:
            commitdb(db)
            return ReturnType(message="Review added successfully", status=201)
        except Exception as e:
            rollbackdb(db)
            print(f"Error adding review: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)

class DocReviewMutation(graphene.ObjectType):
    add_doc_review = AddDocReview.Field()
    