import graphene
from .users import UsersQuery, UsersMutation
from .seniors import SeniorsQuery, SeniorsMutation
from .doctors import DoctorsQuery, DoctorMutation
from .doc_reviews import DocReviewsQuery, DocReviewMutation
from .appointments import AppointmentsQuery, AppointmentsMutation
from .emergency_contacts import EmergencyContactsQuery, EmergencyContactMutation
from .vital_types import VitalTypesQuery, VitalTypesMutation
from .groups import GroupQuery, GroupMutation
from .auth import GetToken, AuthMutation

class Query(UsersQuery, 
            SeniorsQuery,
            DoctorsQuery, 
            AppointmentsQuery, 
            DocReviewsQuery,
            EmergencyContactsQuery,
            VitalTypesQuery,
            GroupQuery,
            GetToken, 
            graphene.ObjectType):
    pass


class Mutation(UsersMutation, 
               SeniorsMutation, 
               DoctorMutation,
               AppointmentsMutation,
               DocReviewMutation,
               EmergencyContactMutation, 
               VitalTypesMutation,  
               GroupMutation,            
               AuthMutation, 
               graphene.ObjectType):
    pass 
    
schema = graphene.Schema(
                            query=Query,
                            mutation=Mutation
                        )
