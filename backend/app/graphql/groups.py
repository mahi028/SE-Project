from graphene_sqlalchemy import SQLAlchemyObjectType
import graphene
from ..models import Group, Joinee, db
from .return_types import ReturnType

class GroupType(SQLAlchemyObjectType):
    class Meta:
        model = Group

class JoineeType(SQLAlchemyObjectType):
    class Meta:
        model = Joinee

# Queries: fetch all groups, groups by admin, and members of a group
class GroupsQuery(graphene.ObjectType):
    get_groups = graphene.List(
        GroupType,
        admin=graphene.Int(),
        pincode=graphene.String()
    )
    get_group_members = graphene.List(JoineeType, grp_id=graphene.Int(required=True))

    def resolve_get_groups(self, info, admin=None, pincode=None):
        query = Group.query
        if admin is not None:
            query = query.filter_by(admin=admin)
        if pincode is not None:
            query = query.filter_by(pincode=pincode)
        return query.all()

    def resolve_get_group_members(self, info, grp_id):
        return Joinee.query.filter_by(grp_id=grp_id).all()

# Mutation: create group (by senior), join group (by senior)
class CreateGroup(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        timing = graphene.DateTime(required=True)
        admin = graphene.Int(required=True)
        pincode = graphene.String()
        location = graphene.String()

    Output = ReturnType

    def mutate(self, info, label, timing, admin, pincode=None, location=None):
        group = Group(
            label=label,
            timing=timing,
            admin=admin,
            pincode=pincode,
            location=location
        )
        db.session.add(group)
        db.session.commit()
        return ReturnType(message="Group created successfully", status=1)

class JoinGroup(graphene.Mutation):
    class Arguments:
        grp_id = graphene.Int(required=True)
        sen_id = graphene.Int(required=True)

    Output = ReturnType

    def mutate(self, info, grp_id, sen_id):
        # Prevent duplicate join
        existing = Joinee.query.filter_by(grp_id=grp_id, sen_id=sen_id).first()
        if existing:
            return ReturnType(message="Already joined", status=0)
        joinee = Joinee(grp_id=grp_id, sen_id=sen_id)
        db.session.add(joinee)
        db.session.commit()
        return ReturnType(message="Joined group successfully", status=1)

class GroupMutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    join_group = JoinGroup.Field()