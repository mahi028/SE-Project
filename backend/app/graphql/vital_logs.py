import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from ..models import VitalLogs, SenInfo, db
from datetime import datetime
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb, deletedb
from ..utils.authControl import get_senior
from ..utils.vital_types_data import get_vital_type_by_id
from .vital_types import VitalTypeType  # Import instead of redefining

class VitalLogType(SQLAlchemyObjectType):
    class Meta:
        model = VitalLogs
    
    # Add the vitalType field that the frontend expects
    vital_type = graphene.Field(VitalTypeType)
    
    def resolve_vital_type(self, info):
        # Get vital type data from hardcoded data
        vital_type_data = get_vital_type_by_id(self.vital_type_id)
        if vital_type_data:
            return VitalTypeType(
                type_id=vital_type_data['type_id'],
                label=vital_type_data['label'],
                unit=vital_type_data['unit'],
                threshold=vital_type_data['threshold']
            )
        return None

class VitalLogsQuery(graphene.ObjectType):
    get_vital_logs = graphene.List(
        VitalLogType,
        sen_id=graphene.Int(required=True),
        vital_type_id=graphene.Int(required=False)
    )
    get_vital_logs_by_senior = graphene.List(VitalLogType)  # Add this query for current senior
    get_vital_log = graphene.Field(VitalLogType, log_id=graphene.Int(required=True))

    def resolve_get_vital_logs(self, info, sen_id, vital_type_id=None):
        query = VitalLogs.query.filter_by(sen_id=sen_id)
        if vital_type_id:
            query = query.filter_by(vital_type_id=vital_type_id)
        return query.order_by(VitalLogs.logged_at.desc()).all()

    def resolve_get_vital_logs_by_senior(self, info):
        # Get current senior from authentication
        senior = get_senior(info)
        if not senior:
            return []
        return VitalLogs.query.filter_by(sen_id=senior.sen_id).order_by(VitalLogs.logged_at.desc()).all()

    def resolve_get_vital_log(self, info, log_id):
        return VitalLogs.query.get(log_id)

class AddVitalLog(graphene.Mutation):
    class Arguments:
        vital_type_id = graphene.Int(required=True)
        reading = graphene.String(required=True)
        logged_at = graphene.DateTime(required=False)
        sen_id = graphene.Int(required=False)  # Optional - will use current user if not provided

    Output = ReturnType

    def mutate(self, info, vital_type_id, reading, logged_at=None, sen_id=None):
        # If sen_id not provided, use current user
        if sen_id is None:
            senior = get_senior(info)
            if not senior:
                return ReturnType(message="Senior not found", status=404)
            sen_id = senior.sen_id
        else:
            senior = SenInfo.query.get(sen_id)
            if not senior:
                return ReturnType(message="Senior not found", status=404)

        # Verify vital type exists in hardcoded data
        vital_type_data = get_vital_type_by_id(vital_type_id)
        if not vital_type_data:
            return ReturnType(message="Vital type not found", status=404)

        # Use current time if not provided
        if logged_at is None:
            logged_at = datetime.now()

        vital_log = VitalLogs(
            sen_id=sen_id,
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
            return ReturnType(message="Error adding vital log", status=500)


class VitalLogsMutation(graphene.ObjectType):
    add_vital_log = AddVitalLog.Field()