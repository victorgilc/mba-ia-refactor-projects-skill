from sqlalchemy import func
from database import db
from models.user import User
from models.task import Task


def list_users():
    users = User.query.all()
    counts = dict(
        db.session.query(Task.user_id, func.count(Task.id))
        .group_by(Task.user_id)
        .all()
    )

    result = []
    for u in users:
        result.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'active': u.active,
            'created_at': str(u.created_at),
            'task_count': counts.get(u.id, 0),
        })
    return result


def find_user(user_id):
    return User.query.get(user_id)


def find_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_tasks(user_id):
    return Task.query.filter_by(user_id=user_id).all()


def create_user(name, email, password, role):
    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user, data):
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    if 'role' in data:
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']
    db.session.commit()
    return user


def delete_user(user):
    tasks = Task.query.filter_by(user_id=user.id).all()
    for t in tasks:
        db.session.delete(t)
    db.session.delete(user)
    db.session.commit()
