from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Roles(Enum):
    SEN = '10'
    DOC = '01'
    MOD = '11'

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class User(db.Model):
    __tablename__ = 'users'
    ez_id = db.Column(db.String(32), primary_key=True)  # format: ez(role)(10auto_num)name
    role = db.Column(db.Enum(Roles), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(8))
    age = db.Column(db.Integer)
    phone_num = db.Column(db.String(10), unique=True, nullable=False)
    alternate_phone_num = db.Column(db.String(10))
    pincode = db.Column(db.String(6))
    # more_address_field = db.Column(db.String(256))  # tbd
    profile_image_url = db.Column(db.String(256))
    
    # Relationships
    sen_info = db.relationship('SenInfo', backref='user', uselist=False)
    doc_info = db.relationship('DocInfo', backref='user', uselist=False)
    reminders = db.relationship('Reminders', backref='user', lazy=True)



class SenInfo(db.Model):
    __tablename__ = 'sen_info'
    sen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    medical_info = db.Column(db.JSON)
    
    # Relationships
    embeddings = db.relationship('Embeddings', backref='sen_info', lazy=True)
    emergency_contacts = db.relationship('EmergencyContacts', backref='sen_info', lazy=True)
    vital_logs = db.relationship('VitalLogs', backref='sen_info', lazy=True)
    appointments = db.relationship('Appointments', backref='sen_info', lazy=True)
    doc_reviews = db.relationship('DocReviews', backref='sen_info', lazy=True)
    groups_admin = db.relationship('Group', backref='admin_sen', foreign_keys='Group.admin', lazy=True)


class Embeddings(db.Model):
    __tablename__ = 'embeddings'
    emb_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    vector = db.Column(db.PickleType)


class EmergencyContacts(db.Model):
    __tablename__ = 'emergency_contacts'
    cont_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone_num = db.Column(db.String(10))
    relationship = db.Column(db.String(64))
    pincode = db.Column(db.String(6))  # tbd


class DocInfo(db.Model):
    __tablename__ = 'doc_info'
    doc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    specialization = db.Column(db.String(128))
    working_hours = db.Column(db.String(128)) # ["9-6", "10-7", "11-8 etc."] 
    appointment_duration = db.Column(db.Integer, default=30)  # in minutes
    consultation_fee = db.Column(db.Float, default=0.0)
    availability_status = db.Column(db.Boolean, default=True)
    prof_info = db.Column(db.JSON) 
    govt_id_url = db.Column(db.String(256))
    med_licence_url = db.Column(db.String(256))
    degree_cert_url = db.Column(db.String(256))
    
    # Relationships
    doc_reviews = db.relationship('DocReviews', backref='doc_info', lazy=True)
    appointments = db.relationship('Appointments', backref='doc_info', lazy=True)


class DocReviews(db.Model):
    __tablename__ = 'doc_reviews'
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'))
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    stars = db.Column(db.Integer)
    review = db.Column(db.Text)



class Reminders(db.Model):
    __tablename__ = 'reminders'
    rem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ez_id = db.Column(db.String(32), db.ForeignKey('users.ez_id'), nullable=False)
    label = db.Column(db.String(128))
    category = db.Column(db.String(32))  # [medic, hyd, group, ...]
    rem_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)



class Appointments(db.Model):
    __tablename__ = 'appointments'
    app_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_info.doc_id'))
    rem_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VitalLogs(db.Model):
    __tablename__ = 'vital_logs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sen_id = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    label = db.Column(db.String(64))
    unit = db.Column(db.String(32))
    value = db.Column(db.Float)
    current_time = db.Column(db.DateTime, default=datetime.utcnow)



class Group(db.Model):
    __tablename__ = 'groups'
    grp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(128))
    timing = db.Column(db.DateTime)
    admin = db.Column(db.Integer, db.ForeignKey('sen_info.sen_id'))
    pincode = db.Column(db.String(6)) 
    location = db.Column(db.String(256))
    joinee = db.Column(db.JSON)  # {sen_id1, sen_id2, ...}


