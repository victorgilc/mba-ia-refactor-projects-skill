from flask import request, jsonify
import re
from utils.helpers import VALID_ROLES, MIN_PASSWORD_LENGTH
from services import task_service, user_service

EMAIL_REGEX = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'


def get_users():
    return jsonify(user_service.list_users()), 200


def get_user(user_id):
    user = user_service.find_user(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = user.to_dict()
    data['tasks'] = [task_service.serialize_base(t) for t in user_service.get_user_tasks(user_id)]
    return jsonify(data), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    if not password:
        return jsonify({'error': 'Senha é obrigatória'}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({'error': 'Email inválido'}), 400

    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400

    if user_service.find_by_email(email):
        return jsonify({'error': 'Email já cadastrado'}), 409

    if role not in VALID_ROLES:
        return jsonify({'error': 'Role inválido'}), 400

    user = user_service.create_user(name, email, password, role)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = user_service.find_user(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'email' in data:
        if not re.match(EMAIL_REGEX, data['email']):
            return jsonify({'error': 'Email inválido'}), 400

        existing = user_service.find_by_email(data['email'])
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email já cadastrado'}), 409

    if 'password' in data and len(data['password']) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': 'Senha muito curta'}), 400

    if 'role' in data and data['role'] not in VALID_ROLES:
        return jsonify({'error': 'Role inválido'}), 400

    user = user_service.update_user(user, data)
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = user_service.find_user(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    user_service.delete_user(user)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    user = user_service.find_user(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = user_service.get_user_tasks(user_id)
    return jsonify([task_service.serialize_short_for_user(t) for t in tasks]), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = user_service.find_by_email(email)
    if not user:
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict()
    }), 200
