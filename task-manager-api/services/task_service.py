from datetime import datetime
from sqlalchemy.orm import joinedload
from database import db
from models.task import Task


def is_overdue(task, now=None):
    now = now or datetime.utcnow()
    return bool(
        task.due_date
        and task.due_date < now
        and task.status not in ('done', 'cancelled')
    )


def serialize_base(task):
    return task.to_dict()


def serialize_detail(task):
    data = task.to_dict()
    data['overdue'] = is_overdue(task)
    return data


def serialize_full(task):
    data = serialize_detail(task)
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def serialize_short_for_user(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': is_overdue(task),
    }


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [serialize_full(t) for t in tasks]


def get_task(task_id):
    return Task.query.get(task_id)


def find_user(user_id):
    from models.user import User
    return User.query.get(user_id)


def find_category(category_id):
    from models.category import Category
    return Category.query.get(category_id)


def create_task(title, description, status, priority, user_id, category_id, due_date, tags):
    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id
    if due_date:
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags
    db.session.add(task)
    db.session.commit()
    return task


def update_task(task, data):
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'user_id' in data:
        task.user_id = data['user_id']
    if 'category_id' in data:
        task.category_id = data['category_id']
    if 'due_date' in data:
        task.due_date = data['due_date']
    if 'tags' in data:
        task.tags = data['tags']
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return task


def delete_task(task):
    db.session.delete(task)
    db.session.commit()


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority is not None:
        tasks = tasks.filter(Task.priority == priority)

    if user_id is not None:
        tasks = tasks.filter(Task.user_id == user_id)

    return tasks.all()


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    now = datetime.utcnow()
    overdue = Task.query.filter(
        Task.due_date < now,
        Task.status.notin_(('done', 'cancelled')),
    ).count()

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }
