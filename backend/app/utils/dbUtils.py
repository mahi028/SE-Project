from app.models import db, User
from datetime import datetime
from sqlalchemy import func, cast, Integer

def adddb(obj: object) -> None:
    db.session.add(obj)

def addBulkdb(objs: list[object]) -> None:
    db.session.add_all(objs)

def deletedb(obj: object) -> None:
    db.session.delete(obj)

def commitdb() -> None:
    db.session.commit()

def rollbackdb() -> None:
    db.session.rollback()

def ez_id_generator(role):
    return f'ez_{role}{str(db.session.query(db.func.max(db.cast(db.func.substr(User.ez_id, 4, 10), db.Integer))).scalar() + 1).zfill(10)}'

ROLE_PREFIXES = {
    0: 'sen',
    1: 'doc',
    # Add other roles as needed
}

def generate_ez_id(role: int) -> str:
    prefix = ROLE_PREFIXES.get(role, 'unk')  # fallback if role is undefined

    now = datetime.now()
    month_code = now.strftime("%y%m")  # YYMM format e.g., '2507'

    # Count existing users with same role and month prefix
    pattern = f'ez-{prefix}-{month_code}-%'
    serial_count = db.session.query(func.count()).filter(User.ez_id.like(pattern)).scalar() or 0

    serial = str(serial_count + 1).zfill(4)  # Zero-pad to 4 digits

    return f'ez-{prefix}-{month_code}-{serial}'
