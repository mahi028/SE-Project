from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import DocReviews, db
from .return_types import ReturnType

class DocReviewType(SQLAlchemyObjectType):
    class Meta:
        model = DocReviews

# Query for getting reviews by doctor ID
class Query(graphene.ObjectType):
    get_doc_reviews = graphene.List(DocReviewType, doc_id=graphene.Int(required=True))

    def resolve_get_doc_reviews(self, info, doc_id):
        return DocReviews.query.filter_by(doc_id=doc_id).all()

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
        db.session.add(doc_review)
        db.session.commit()
        return ReturnType(message="Review added successfully", status=1)

# Mutation for updating a doctor review
class UpdateDocReview(graphene.Mutation):
    class Arguments:
        review_id = graphene.Int(required=True)
        rating = graphene.Int()
        review = graphene.String()

    Output = ReturnType

    def mutate(self, info, review_id, rating=None, review=None):
        doc_review = DocReviews.query.filter_by(review_id=review_id).first()
        if not doc_review:
            return ReturnType(message="Review not found", status=0)
        if rating is not None:
            doc_review.rating = rating
        if review is not None:
            doc_review.review = review
        db.session.commit()
        return ReturnType(message="Review updated successfully", status=1)

class Mutation(graphene.ObjectType):
    add_doc_review = AddDocReview.Field()
    update_doc_review = UpdateDocReview.Field()