from functools import wraps
from flask_jwt_extended import jwt_required, current_user
from flask import request, abort
from ..models import User

def get_user(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    user = User.query.get(ez_id)
    return user

def get_senior(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    senior = User.query.get(ez_id)
    if senior.role != 0:
        raise Exception("UnAuthorised Access! Senior Only.")
    if not senior.sen_info:
        raise Exception("Senior Profile Not Complete!.")
    return senior

def get_doctor(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    doctor = User.query.get(ez_id)
    if doctor.role != 1:
        raise Exception("UnAuthorised Access! Doctors Only.")
    if not doctor.doc_info:
        raise Exception("Doctor Profile Not Complete!.")
    return doctor

def get_mod(info):
    ez_id = info.context.get("current_user")
    if not ez_id:
        raise Exception("Authentication required")
    mod = User.query.get(ez_id)
    if mod.role != 2:
        raise Exception("UnAuthorised Access! Moderators Only.")
    return mod