import graphene
from .users import UsersQuery, UsersMutation
from .seniors import SeniorsQuery, SeniorsMutation
from .doctors import DoctorsQuery, DoctorMutation
from .doc_reviews import DocReviewsQuery, DocReviewMutation
from .appointments import AppointmentsQuery, AppointmentsMutation
from .emergency_contacts import EmergencyContactsQuery, EmergencyContactMutation
from .groups import GroupsQuery, GroupMutation
from .auth import GetToken, AuthMutation

class Query(UsersQuery, 
            SeniorsQuery,
            DoctorsQuery, 
            AppointmentsQuery, 
            DocReviewsQuery,
            EmergencyContactsQuery,
            GroupsQuery,
            GetToken, 
            graphene.ObjectType):
    pass


class Mutation(UsersMutation, 
               SeniorsMutation, 
               DoctorMutation,
               AppointmentsMutation,
               DocReviewMutation,
               EmergencyContactMutation,   
               GroupMutation,            
               AuthMutation, 
               graphene.ObjectType):
    pass 
    
schema = graphene.Schema(
                            query=Query,
                            mutation=Mutation
                        )
