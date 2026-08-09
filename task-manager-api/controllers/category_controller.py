from flask import request, jsonify
from utils.helpers import DEFAULT_COLOR
from services import category_service


def get_categories():
    return jsonify(category_service.list_categories()), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    category = category_service.create_category(
        name,
        data.get('description', ''),
        data.get('color', DEFAULT_COLOR),
    )
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    cat = category_service.find_category(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json() or {}
    cat = category_service.update_category(cat, data)
    return jsonify(cat.to_dict()), 200


def delete_category(cat_id):
    cat = category_service.find_category(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    category_service.delete_category(cat)
    return jsonify({'message': 'Categoria deletada'}), 200
