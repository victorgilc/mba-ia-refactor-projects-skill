from sqlalchemy import func
from database import db
from models.category import Category
from models.task import Task


def list_categories():
    categories = Category.query.all()
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )

    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = counts.get(c.id, 0)
        result.append(data)
    return result


def find_category(cat_id):
    return Category.query.get(cat_id)


def create_category(name, description, color):
    category = Category()
    category.name = name
    category.description = description
    category.color = color
    db.session.add(category)
    db.session.commit()
    return category


def update_category(cat, data):
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']
    db.session.commit()
    return cat


def delete_category(cat):
    db.session.delete(cat)
    db.session.commit()
