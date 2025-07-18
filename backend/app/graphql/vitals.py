from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import VitalTypes, VitalLogs, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb

class VitalTypeType(SQLAlchemyObjectType):
    class Meta:
        model = VitalTypes

class VitalLogType(SQLAlchemyObjectType):
    class Meta:
        model = VitalLogs

# Query for fetching all vital types and logs for a senior
class Query(graphene.ObjectType):
    get_vital_types = graphene.List(VitalTypeType)
    get_vital_logs = graphene.List(VitalLogType, sen_id=graphene.Int(required=True))

    evaluate_vital_status = graphene.Field(
        graphene.JSONString,
        vital_type=graphene.String(required=True),
        reading=graphene.String(required=True)
    )

    def resolve_get_vital_types(self, info):
        return VitalTypes.query.all()

    def resolve_get_vital_logs(self, info, sen_id):
        return VitalLogs.query.filter_by(sen_id=sen_id).all()

# Mutation for adding a vital log
class AddVitalLog(graphene.Mutation):
    class Arguments:
        sen_id = graphene.Int(required=True)
        vital_type_id = graphene.Int(required=True)
        reading = graphene.String(required=True)
        logged_at = graphene.DateTime()  # Optional, can be set by server

    Output = ReturnType

    def mutate(self, info, sen_id, vital_type_id, reading, logged_at=None):
        log = VitalLogs(
            sen_id=sen_id,
            vital_type_id=vital_type_id,
            reading=reading,
            logged_at=logged_at
        )
        adddb(log)
        
        try:
            commitdb(db)
            return ReturnType(message="Vital log added successfully", status=1)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error adding vital log: {str(e)}", status=403)

class Mutation(graphene.ObjectType):
    add_vital_log = AddVitalLog.Field()
