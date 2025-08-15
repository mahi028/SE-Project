from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Group, Joinee, SenInfo, db
from .return_types import ReturnType
from ..utils.dbUtils import adddb, commitdb, rollbackdb
from ..utils.authControl import get_senior

class GroupType(SQLAlchemyObjectType):
    class Meta:
        model = Group

class JoineeType(SQLAlchemyObjectType):
    class Meta:
        model = Joinee

class GroupsQuery(graphene.ObjectType):
    get_groups = graphene.List(
        GroupType, 
        pincode=graphene.String(required=False),
        admin_id=graphene.Int(required=False)
    )
    get_group_members = graphene.List(JoineeType, grp_id=graphene.Int(required=True))

    def resolve_get_groups(self, info, pincode=None, admin_id=None):
        query = Group.query
        
        if admin_id:
            # Get groups created by specific admin
            query = query.filter(Group.admin == admin_id)
        elif pincode:
            # Get groups in specific pincode
            query = query.filter(Group.pincode == pincode)
        else:
            # Default: get all groups
            pass
            
        return query.all()

    def resolve_get_group_members(self, info, grp_id):
        return Joinee.query.filter_by(grp_id=grp_id).all()

class CreateGroup(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        timing = graphene.DateTime(required=True)
        pincode = graphene.String(required=False)
        location = graphene.String(required=False)

    Output = ReturnType

    def mutate(self, info, label, timing, pincode=None, location=None):
        senior = get_senior(info)
        if not senior:
            return ReturnType(message="Senior citizen not found", status=404)

        # Use senior's pincode if not provided
        if not pincode:
            pincode = senior.pincode

        group = Group(
            label=label,
            timing=timing,
            admin=senior.sen_id,
            pincode=pincode,
            location=location
        )
        
        adddb(group)
        try:
            commitdb()
            return ReturnType(message="Group created successfully", status=1)
        except Exception as e:
            rollbackdb()
            print(f"Error creating group: {e}")
            return ReturnType(message="Failed to create group", status=0)

class JoinGroup(graphene.Mutation):
    class Arguments:
        grp_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, grp_id):
        senior = get_senior(info)
        if not senior:
            return ReturnType(message="Senior citizen not found", status=404)

        # Check if group exists
        group = Group.query.get(grp_id)
        if not group:
            return ReturnType(message="Group not found", status=404)

        # Check if already joined
        existing_member = Joinee.query.filter_by(
            grp_id=grp_id, 
            sen_id=senior.sen_id
        ).first()
        
        if existing_member:
            return ReturnType(message="You are already a member of this group", status=0)

        # Add member
        member = Joinee(
            grp_id=grp_id,
            sen_id=senior.sen_id
        )
        
        adddb(member)
        try:
            commitdb()
            return ReturnType(message="Successfully joined the group", status=1)
        except Exception as e:
            rollbackdb()
            print(f"Error joining group: {e}")
            return ReturnType(message="Failed to join group", status=0)

class GroupsMutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()
