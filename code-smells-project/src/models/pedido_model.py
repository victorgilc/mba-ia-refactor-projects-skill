from src.models.database import get_db

# Constantes para Relatório de Vendas (AP-16 — Magic Numbers)
FA_LIMITE_ALTO = 10000
DESCONTO_ALTO = 0.1
FA_LIMITE_MEDIO = 5000
DESCONTO_MEDIO = 0.05
FA_LIMITE_BAIXO = 1000
DESCONTO_BAIXO = 0.02

def _obter_itens_pedido(db, pedido_id):
    """Itens de um pedido em UMA query com JOIN (AP-13/Padrão 8 — sem N+1)."""
    cursor_item = db.cursor()
    cursor_item.execute(
        "SELECT it.*, p.nome AS produto_nome "
        "FROM itens_pedido it "
        "LEFT JOIN produtos p ON p.id = it.produto_id "
        "WHERE it.pedido_id = ?",
        (pedido_id,)
    )
    itens_rows = cursor_item.fetchall()

    itens = []
    for row in itens_rows:
        itens.append({
            "produto_id": row["produto_id"],
            "produto_nome": row["produto_nome"] if row["produto_nome"] else "Desconhecido",
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"]
        })
    return itens

def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()
    total = 0

    # Validar produtos e estoques antes de prosseguir
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    # Inserir pedido
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total)
    )
    pedido_id = cursor.lastrowid

    # Inserir itens do pedido e atualizar estoque
    for item in itens:
        cursor.execute("SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"])
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}

def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        pedido_id = row["id"]
        pedido = {
            "id": pedido_id,
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": _obter_itens_pedido(db, pedido_id)
        }
        result.append(pedido)
    return result

def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos")
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        pedido_id = row["id"]
        pedido = {
            "id": pedido_id,
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": _obter_itens_pedido(db, pedido_id)
        }
        result.append(pedido)
    return result

def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id)
    )
    db.commit()
    return True

def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento_row = cursor.fetchone()
    faturamento = faturamento_row[0] if faturamento_row and faturamento_row[0] is not None else 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    # Cálculo dos descontos usando constantes expressivas (AP-16)
    desconto = 0
    if faturamento > FA_LIMITE_ALTO:
        desconto = faturamento * DESCONTO_ALTO
    elif faturamento > FA_LIMITE_MEDIO:
        desconto = faturamento * DESCONTO_MEDIO
    elif faturamento > FA_LIMITE_BAIXO:
        desconto = faturamento * DESCONTO_BAIXO

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    }

def contar_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    return cursor.fetchone()[0]

