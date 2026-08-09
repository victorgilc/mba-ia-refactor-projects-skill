from flask import jsonify
from services import report_service


def summary_report():
    return jsonify(report_service.summary()), 200


def user_report(user_id):
    report = report_service.user_report(user_id)
    if report is None:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(report), 200
