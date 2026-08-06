import sqlite3
from flask import g
from werkzeug.security import generate_password_hash
from src.config.settings import DATABASE_PATH

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    try:
        app.teardown_appcontext(close_db)
    except AssertionError:
        pass # Se já iniciou o primeiro request (comum em testes), não re-registra
    
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Criar tabelas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                descricao TEXT,
                preco REAL,
                estoque INTEGER,
                categoria TEXT,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                senha TEXT,
                tipo TEXT DEFAULT 'cliente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                status TEXT DEFAULT 'pendente',
                total REAL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto_id INTEGER,
                quantidade INTEGER,
                preco_unitario REAL
            )
        """)
        db.commit()

        # Seed Produtos
        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            produtos = [
                ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
                ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
                ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
                ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
                ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
                ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
                ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
                ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
                ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
                ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
            ]
            cursor.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                produtos
            )
            db.commit()

        # Seed Usuários com hash de senha
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            usuarios = [
                ("Admin", "admin@loja.com", generate_password_hash("admin123"), "admin"),
                ("João Silva", "joao@email.com", generate_password_hash("123456"), "cliente"),
                ("Maria Santos", "maria@email.com", generate_password_hash("senha123"), "cliente"),
            ]
            cursor.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                usuarios
            )
            db.commit()
        else:
            # Migração de senhas em texto puro já existentes para hashes seguros
            cursor.execute("SELECT id, senha FROM usuarios")
            usuarios_existentes = cursor.fetchall()
            for usuario in usuarios_existentes:
                senha_atual = usuario["senha"]
                if not (senha_atual.startswith("scrypt:") or senha_atual.startswith("pbkdf2:") or senha_atual.startswith("sha256:")):
                    # É texto puro! Vamos aplicar hash
                    senha_hash = generate_password_hash(senha_atual)
                    cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario["id"]))
            db.commit()

def reset_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass # Se a tabela sqlite_sequence ainda não existir, ignora
    db.commit()


