from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import VitalTypes, db
from .return_types import ReturnType
from utils.dbUtils import adddb, commitdb, rollbackdb

class VitalTypeType(SQLAlchemyObjectType):
    class Meta:
        model = VitalTypes

class VitalTypesQuery(graphene.ObjectType):
    get_vital_types = graphene.List(VitalTypeType)
    get_vital_type = graphene.Field(VitalTypeType, type_id=graphene.Int(required=True))

    def resolve_get_vital_types(self, info):
        return VitalTypes.query.all()

    def resolve_get_vital_type(self, info, type_id):
        return VitalTypes.query.get(type_id)


class AddVitalType(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        unit = graphene.String(required=True)
        threshold = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, label, unit, threshold=None):
        # Check if vital type with same label exists
        if VitalTypes.query.filter_by(label=label).first():
            return ReturnType(message="Vital type with this label already exists", status=0)

        vital_type = VitalTypes(
            label=label,
            unit=unit,
            threshold=threshold
        )
        
        adddb(vital_type)
        try:
            commitdb(db)
            return ReturnType(message="Vital type added successfully", status=1)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error adding vital type: {str(e)}", status=0)


class UpdateVitalType(graphene.Mutation):
    class Arguments:
        type_id = graphene.Int(required=True)
        label = graphene.String()
        unit = graphene.String()
        threshold = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, type_id, **kwargs):
        vital_type = VitalTypes.query.get(type_id)
        if not vital_type:
            return ReturnType(message="Vital type not found", status=0)

        # Check if updating label conflicts with existing
        if 'label' in kwargs:
            existing = VitalTypes.query.filter(
                VitalTypes.label == kwargs['label'],
                VitalTypes.type_id != type_id
            ).first()
            if existing:
                return ReturnType(message="Vital type with this label already exists", status=0)

        for key, value in kwargs.items():
            if value is not None:
                setattr(vital_type, key, value)

        try:
            commitdb(db)
            return ReturnType(message="Vital type updated successfully", status=1)
        except Exception as e:
            rollbackdb(db)
            return ReturnType(message=f"Error updating vital type: {str(e)}", status=0)

class VitalTypesMutation(graphene.ObjectType):
    add_vital_type = AddVitalType.Field()
    update_vital_type = UpdateVitalType.Field()