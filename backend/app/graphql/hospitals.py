from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Hospitals, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb


class HospitalType(SQLAlchemyObjectType):
    class Meta:
        model = Hospitals


class HospitalsQuery(graphene.ObjectType):
    get_hospitals = graphene.List(HospitalType, pincode=graphene.String(required=True))

    def resolve_get_hospitals(self, info, pincode):
        return Hospitals.query.filter_by(pincode=pincode).all()


class AddHospital(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        address = graphene.String(required=True)
        pincode = graphene.String(required=True)
        phone = graphene.String()
        email = graphene.String()
        h_type = graphene.String()
        services = graphene.JSONString()
        coordinates = graphene.JSONString()

    Output = ReturnType

    def mutate(self, info, name, address, pincode, phone=None, email=None, h_type=None, services=None, coordinates=None):
        # Check if hospital already exists
        hospital = Hospitals(
            name=name,
            address=address,
            pincode=pincode,
            phone=phone,
            email=email,
            h_type=h_type,
            services=services,
            coordinates=coordinates
        )
        
        adddb(hospital)
        
        try:
            commitdb()
            return ReturnType(message="Hospital added successfully", status=201)
        except Exception as e:
            rollbackdb()
            print(f"Error adding hospital: {str(e)}")
            return ReturnType(message="Error adding hospital", status=500)


class HospitalsMutation(graphene.ObjectType):
    add_hospital = AddHospital.Field()
