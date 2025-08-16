import graphene
from .return_types import ReturnType
from ..utils.vital_types_data import get_vital_types, get_vital_type_by_id

class VitalTypeType(graphene.ObjectType):
    type_id = graphene.Int()
    label = graphene.String()
    unit = graphene.String()
    threshold = graphene.JSONString()

class VitalTypesQuery(graphene.ObjectType):
    get_vital_types = graphene.List(VitalTypeType)
    get_vital_type = graphene.Field(VitalTypeType, type_id=graphene.Int(required=True))

    def resolve_get_vital_types(self, info):
        """Return hardcoded vital types data."""
        vital_types_data = get_vital_types()
        return [VitalTypeType(**vt) for vt in vital_types_data]

    def resolve_get_vital_type(self, info, type_id):
        """Return a specific vital type by ID."""
        vital_type_data = get_vital_type_by_id(type_id)
        if vital_type_data:
            return VitalTypeType(**vital_type_data)
        return None

# No mutations needed for hardcoded data
class VitalTypesMutation(graphene.ObjectType):
    pass