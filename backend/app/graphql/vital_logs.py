import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..models import VitalLogs, VitalTypes, SenInfo, db
from datetime import datetime
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from ..utils.authControl import get_senior

class VitalLogType(SQLAlchemyObjectType):
    class Meta:
        model = VitalLogs

class VitalLogsQuery(graphene.ObjectType):
    get_vital_logs = graphene.List(
        VitalLogType,
        sen_id=graphene.Int(required=True),
        vital_type_id=graphene.Int(required=False)
    )
    get_vital_log = graphene.Field(VitalLogType, log_id=graphene.Int(required=True))

    def resolve_get_vital_logs(self, info, sen_id, vital_type_id=None):
        query = VitalLogs.query.filter_by(sen_id=sen_id)
        if vital_type_id:
            query = query.filter_by(vital_type_id=vital_type_id)
        return query.order_by(VitalLogs.logged_at.desc()).all()

    def resolve_get_vital_log(self, info, log_id):
        return VitalLogs.query.get(log_id)

class AddVitalLog(graphene.Mutation):
    class Arguments:
        vital_type_id = graphene.Int(required=True)
        reading = graphene.String(required=True)
        logged_at = graphene.DateTime()

    Output = ReturnType

    def mutate(self, info, vital_type_id, reading, logged_at=None):
        # Validate senior exists
        senior = get_senior(info)

        # Validate vital type exists
        vital_type = VitalTypes.query.get(vital_type_id)
        if not vital_type:
            return ReturnType(message="Vital type not found", status=0)

        # If logged_at not provided, use current time
        if not logged_at:
            logged_at = datetime.utcnow()

        vital_log = VitalLogs(
            sen_id=senior.sen_id,
            vital_type_id=vital_type_id,
            reading=reading,
            logged_at=logged_at
        )

        adddb(vital_log)
        try:
            commitdb()
            return ReturnType(message="Vital log added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding vital log: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)


class VitalLogsMutation(graphene.ObjectType):
    add_vital_log = AddVitalLog.Field()