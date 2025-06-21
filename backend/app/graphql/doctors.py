from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import User,DocInfo, db
from .return_types import ReturnType

class DoctorType(SQLAlchemyObjectType):
    class Meta:
        model = DocInfo

class GetDoctors(graphene.ObjectType):
    all_doctors = graphene.List(DoctorType)
    doctor = graphene.Field(DoctorType, id=graphene.Int(), specialization=graphene.String())

    def resolve_all_doctors(self, info):
        return DocInfo.query.all()
    
    def resolve_user(self, info, id=None, specialization=None):
        query = DocInfo.query
        if id:
            return query.filter(DocInfo.doc_id == id).first()
        if specialization:
            return query.filter(DocInfo.specialization == specialization).first()
        return None