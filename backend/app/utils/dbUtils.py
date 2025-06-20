from app.models import db, User

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