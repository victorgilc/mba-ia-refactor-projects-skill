from flask import request, jsonify
from datetime import datetime
from utils.helpers import VALID_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH
from services import task_service


def get_tasks():
    return jsonify(task_service.list_tasks()), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    return jsonify(task_service.serialize_detail(task)), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title')
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    if len(title) < MIN_TITLE_LENGTH:
        return jsonify({'error': 'Título muito curto'}), 400
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({'error': 'Título muito longo'}), 400

    description = data.get('description', '')
    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    if status not in VALID_STATUSES:
        return jsonify({'error': 'Status inválido'}), 400

    try:
        priority = int(priority)
    except (TypeError, ValueError):
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
    if priority < 1 or priority > 5:
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

    if user_id:
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Usuário não encontrado'}), 404
        if not task_service.find_user(user_id):
            return jsonify({'error': 'Usuário não encontrado'}), 404

    if category_id:
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Categoria não encontrada'}), 404
        if not task_service.find_category(category_id):
            return jsonify({'error': 'Categoria não encontrada'}), 404

    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

    task = task_service.create_task(
        title, description, status, priority, user_id, category_id, due_date, tags
    )
    return jsonify(task_service.serialize_base(task)), 201


def update_task(task_id):
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'title' in data:
        if len(data['title']) < MIN_TITLE_LENGTH:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(data['title']) > MAX_TITLE_LENGTH:
            return jsonify({'error': 'Título muito longo'}), 400

    if 'status' in data and data['status'] not in VALID_STATUSES:
        return jsonify({'error': 'Status inválido'}), 400

    if 'priority' in data:
        try:
            priority = int(data['priority'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        if priority < 1 or priority > 5:
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        data['priority'] = priority

    if 'user_id' in data:
        user_id = data['user_id']
        if user_id:
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return jsonify({'error': 'Usuário não encontrado'}), 404
            if not task_service.find_user(user_id):
                return jsonify({'error': 'Usuário não encontrado'}), 404
        data['user_id'] = user_id

    if 'category_id' in data:
        category_id = data['category_id']
        if category_id:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                return jsonify({'error': 'Categoria não encontrada'}), 404
            if not task_service.find_category(category_id):
                return jsonify({'error': 'Categoria não encontrada'}), 404
        data['category_id'] = category_id

    if 'due_date' in data:
        if data['due_date']:
            try:
                datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Formato de data inválido'}), 400
        else:
            data['due_date'] = None

    task = task_service.update_task(task, data)
    return jsonify(task_service.serialize_base(task)), 200


def delete_task(task_id):
    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    task_service.delete_task(task)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    priority_raw = request.args.get('priority', '')
    user_id_raw = request.args.get('user_id', '')

    priority = None
    if priority_raw:
        try:
            priority = int(priority_raw)
        except ValueError:
            return jsonify({'error': 'Prioridade inválida'}), 400

    user_id = None
    if user_id_raw:
        try:
            user_id = int(user_id_raw)
        except ValueError:
            return jsonify({'error': 'Usuário inválido'}), 400

    results = task_service.search_tasks(query, status, priority, user_id)
    return jsonify([task_service.serialize_base(t) for t in results]), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
