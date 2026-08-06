from flask import jsonify
from src.models import produto_model, usuario_model, pedido_model

def relatorio_vendas():
    relatorio = pedido_model.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200

def health_check():
    # Usar camada de modelagem em vez de cursor direto no controller (AP-06)
    produtos_count = produto_model.contar_produtos()
    usuarios_count = usuario_model.contar_usuarios()
    pedidos_count = pedido_model.contar_pedidos()

    # Omitir informações confidenciais que vazam infraestrutura/segredos (AP-10 — Resposta vazando Segredos)
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produtos_count,
            "usuarios": usuarios_count,
            "pedidos": pedidos_count
        },
        "versao": "1.0.0",
        "ambiente": "producao"
    }), 200
