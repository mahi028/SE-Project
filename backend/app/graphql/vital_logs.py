import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..models import VitalLogs, VitalTypes, SenInfo, db
from datetime import datetime
from .return_types import ReturnType
from utils.dbUtils import adddb, commitdb, rollbackdb, deletedb

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
        sen_id = graphene.Int(required=True)
        vital_type_id = graphene.Int(required=True)
        reading = graphene.String(required=True)
        logged_at = graphene.DateTime()

    Output = ReturnType

    def mutate(self, info, sen_id, vital_type_id, reading, logged_at=None):
        # Validate senior exists
        senior = SenInfo.query.get(sen_id)
        if not senior:
            return ReturnType(message="Senior not found", status=0)

        # Validate vital type exists
        vital_type = VitalTypes.query.get(vital_type_id)
        if not vital_type:
            return ReturnType(message="Vital type not found", status=0)

        # If logged_at not provided, use current time
        if not logged_at:
            logged_at = datetime.utcnow()

        vital_log = VitalLogs(
            sen_id=sen_id,
            vital_type_id=vital_type_id,
            reading=reading,
            logged_at=logged_at
        )

        adddb(vital_log)
        try:
            commitdb(db)
            return ReturnType(message="Vital log added successfully", status=201)
        except Exception as e:
            rollbackdb(db)
            print(f"Error adding vital log: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)

class UpdateVitalLog(graphene.Mutation):
    class Arguments:
        log_id = graphene.Int(required=True)
        reading = graphene.String()
        logged_at = graphene.DateTime()

    Output = ReturnType

    def mutate(self, info, log_id, **kwargs):
        vital_log = VitalLogs.query.get(log_id)
        if not vital_log:
            return ReturnType(message="Vital log not found", status=0)

        for key, value in kwargs.items():
            if value is not None:
                setattr(vital_log, key, value)

        try:
            commitdb(db)
            return ReturnType(message="Vital log updated successfully", status=200)
        except Exception as e:
            rollbackdb(db)
            print(f"Error updating vital log: {str(e)}")
            return ReturnType(message=f"Something went wrong", status=403)

class DeleteVitalLog(graphene.Mutation):
    class Arguments:
        log_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, log_id):
        vital_log = VitalLogs.query.get(log_id)
        if not vital_log:
            return ReturnType(message="Vital log not found", status=0)

        deletedb(vital_log)

        try:
            commitdb(db)
            return ReturnType(message="Vital log deleted successfully", status=200)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error deleting vital log", status=0)

class VitalLogsMutation(graphene.ObjectType):
    add_vital_log = AddVitalLog.Field()
    update_vital_log = UpdateVitalLog.Field()
    delete_vital_log = DeleteVitalLog.Field()