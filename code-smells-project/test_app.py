import unittest
import json
from app import app
from src.models import database

class TestAppParity(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.client = app.test_client()
        
        # Resetar o banco de dados antes de cada teste para garantir isolamento e paridade limpa
        with app.app_context():
            database.reset_db()
            # Reiniciar tabelas e seed data original
            database.init_db(app)

    def test_01_index(self):
        """GET / -> Retorna JSON de boas-vindas"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertIn("mensagem", dados)
        self.assertEqual(dados["versao"], "1.0.0")

    def test_02_listar_produtos(self):
        """GET /produtos -> Lista todos os produtos"""
        response = self.client.get("/produtos")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertTrue(dados["sucesso"])
        self.assertGreater(len(dados["dados"]), 0)

    def test_03_buscar_produto_por_id(self):
        """GET /produtos/<id> -> Retorna produto existente ou 404"""
        # Produto ID 1 (Notebook Gamer de seed)
        response = self.client.get("/produtos/1")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertEqual(dados["dados"]["nome"], "Notebook Gamer")

        # Produto ID inexistente
        response = self.client.get("/produtos/999")
        self.assertEqual(response.status_code, 404)
        dados = json.loads(response.data)
        self.assertFalse(dados["sucesso"])
        self.assertEqual(dados["erro"], "Produto não encontrado")

    def test_04_criar_produto_validacoes(self):
        """POST /produtos -> Testar regras de validação de criação de produtos"""
        # Sem dados
        response = self.client.post("/produtos", json=None)
        self.assertEqual(response.status_code, 400)

        # Sem campo obrigatório 'nome'
        response = self.client.post("/produtos", json={"preco": 100, "estoque": 10})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Nome", json.loads(response.data)["erro"])

        # Preço negativo
        response = self.client.post("/produtos", json={"nome": "Teclado", "preco": -10, "estoque": 10})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)["erro"], "Preço não pode ser negativo")

        # Estoque negativo
        response = self.client.post("/produtos", json={"nome": "Teclado", "preco": 10, "estoque": -5})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)["erro"], "Estoque não pode ser negativo")

        # Categoria inválida
        response = self.client.post("/produtos", json={"nome": "Teclado", "preco": 10, "estoque": 5, "categoria": "comida"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Categoria inválida", json.loads(response.data)["erro"])

        # Nome muito curto
        response = self.client.post("/produtos", json={"nome": "A", "preco": 10, "estoque": 5})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data)["erro"], "Nome muito curto")

        # Sucesso
        payload = {"nome": "Novo Teclado RGB", "preco": 350.00, "estoque": 20, "categoria": "informatica"}
        response = self.client.post("/produtos", json=payload)
        self.assertEqual(response.status_code, 201)
        dados = json.loads(response.data)
        self.assertTrue(dados["sucesso"])
        self.assertIn("id", dados["dados"])

    def test_05_atualizar_produto(self):
        """PUT /produtos/<id> -> Atualiza produto existente com validações"""
        # ID inexistente
        response = self.client.put("/produtos/999", json={"nome": "A", "preco": 10, "estoque": 5})
        self.assertEqual(response.status_code, 404)

        # ID existente, dados válidos
        payload = {"nome": "Notebook Gamer Pro", "preco": 6500.00, "estoque": 8}
        response = self.client.put("/produtos/1", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Validar alteração
        response = self.client.get("/produtos/1")
        dados = json.loads(response.data)
        self.assertEqual(dados["dados"]["nome"], "Notebook Gamer Pro")
        self.assertEqual(dados["dados"]["preco"], 6500.00)

    def test_06_deletar_produto(self):
        """DELETE /produtos/<id> -> Deleta produto"""
        # ID inexistente
        response = self.client.delete("/produtos/999")
        self.assertEqual(response.status_code, 404)

        # ID existente
        response = self.client.delete("/produtos/2")
        self.assertEqual(response.status_code, 200)

        # Confirmar remoção
        response = self.client.get("/produtos/2")
        self.assertEqual(response.status_code, 404)

    def test_07_buscar_produtos_filtros(self):
        """GET /produtos/busca -> Testa busca com query params"""
        response = self.client.get("/produtos/busca?q=Gamer")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertEqual(dados["total"], 3) # Notebook Gamer, Headset Gamer e Cadeira Gamer de seed

        response = self.client.get("/produtos/busca?categoria=moveis")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertEqual(dados["total"], 1) # Cadeira Gamer

    def test_08_listar_e_buscar_usuarios(self):
        """GET /usuarios -> Lista usuários, GET /usuarios/<id> -> Busca usuário"""
        response = self.client.get("/usuarios")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertGreater(len(dados["dados"]), 0)

        response = self.client.get("/usuarios/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)["dados"]["email"], "admin@loja.com")

    def test_09_criar_usuario_e_login(self):
        """POST /usuarios -> Cria usuário, POST /login -> Realiza login seguro"""
        # Criar usuário
        payload = {"nome": "Carlos Souza", "email": "carlos@gmail.com", "senha": "mypassword123"}
        response = self.client.post("/usuarios", json=payload)
        self.assertEqual(response.status_code, 201)
        usuario_id = json.loads(response.data)["dados"]["id"]

        # Testar login do usuário recém criado
        response = self.client.post("/login", json={"email": "carlos@gmail.com", "senha": "mypassword123"})
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertTrue(dados["sucesso"])
        self.assertEqual(dados["dados"]["nome"], "Carlos Souza")

        # Testar login do usuário antigo pré-existente no seed (admin@loja.com / admin123)
        # Isso garante que a migração transparente de texto puro para hashes está funcionando!
        response = self.client.post("/login", json={"email": "admin@loja.com", "senha": "admin123"})
        self.assertEqual(response.status_code, 200)
        
        # Login incorreto
        response = self.client.post("/login", json={"email": "admin@loja.com", "senha": "senha_errada"})
        self.assertEqual(response.status_code, 401)

    def test_10_pedidos_fluxo(self):
        """POST /pedidos -> Cria pedido com validações e checagem de estoque"""
        # Criar pedido válido
        payload = {
            "usuario_id": 2,
            "itens": [
                {"produto_id": 1, "quantidade": 2}, # Notebook Gamer (Preço: 5999.99, Estoque: 10)
                {"produto_id": 2, "quantidade": 5}  # Mouse Wireless (Preço: 89.90, Estoque: 50)
            ]
        }
        response = self.client.post("/pedidos", json=payload)
        self.assertEqual(response.status_code, 201)
        dados = json.loads(response.data)
        self.assertTrue(dados["sucesso"])
        pedido_id = dados["dados"]["pedido_id"]
        # Total esperado: (5999.99 * 2) + (89.90 * 5) = 11999.98 + 449.50 = 12449.48
        self.assertAlmostEqual(dados["dados"]["total"], 12449.48, places=2)

        # Checar se estoque reduziu
        response = self.client.get("/produtos/1")
        self.assertEqual(json.loads(response.data)["dados"]["estoque"], 8)

        # Tentar comprar com estoque insuficiente
        payload_insuficiente = {
            "usuario_id": 2,
            "itens": [{"produto_id": 1, "quantidade": 10}]
        }
        response = self.client.post("/pedidos", json=payload_insuficiente)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Estoque insuficiente", json.loads(response.data)["erro"])

    def test_11_atualizar_status_pedido(self):
        """PUT /pedidos/<id>/status -> Altera o status do pedido"""
        # Criar pedido
        payload = {"usuario_id": 2, "itens": [{"produto_id": 3, "quantidade": 1}]}
        response = self.client.post("/pedidos", json=payload)
        pedido_id = json.loads(response.data)["dados"]["pedido_id"]

        # Atualizar para status válido
        response = self.client.put(f"/pedidos/{pedido_id}/status", json={"status": "aprovado"})
        self.assertEqual(response.status_code, 200)

        # Atualizar para status inválido
        response = self.client.put(f"/pedidos/{pedido_id}/status", json={"status": "entregando"})
        self.assertEqual(response.status_code, 400)

    def test_12_relatorios(self):
        """GET /relatorios/vendas -> Gera relatório correto"""
        # Fazer pedidos para gerar faturamento e testar o cálculo dos descontos e tickets
        self.client.post("/pedidos", json={"usuario_id": 2, "itens": [{"produto_id": 1, "quantidade": 2}]}) # faturamento 11999.98
        
        response = self.client.get("/relatorios/vendas")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)["dados"]
        self.assertEqual(dados["total_pedidos"], 1)
        self.assertAlmostEqual(dados["faturamento_bruto"], 11999.98, places=2)
        # Desconto acima de 10000 é 10%: 11999.98 * 0.1 = 1199.998 -> round(1200.00)
        self.assertAlmostEqual(dados["desconto_aplicavel"], 1200.00, places=2)

    def test_13_health_check_secure(self):
        """GET /health -> Retorna diagnóstico seguro sem vazamentos de AP-10"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        dados = json.loads(response.data)
        self.assertEqual(dados["status"], "ok")
        self.assertEqual(dados["database"], "connected")
        # Garantir segurança contra vazamento de segredos/infraestrutura (AP-10)
        self.assertNotIn("secret_key", dados)
        self.assertNotIn("db_path", dados)
        self.assertNotIn("debug", dados)

    def test_14_admin_query_secure(self):
        """POST /admin/query -> Retorna 403 Forbidden protegendo de AP-09"""
        response = self.client.post("/admin/query", json={"sql": "SELECT * FROM usuarios"})
        self.assertEqual(response.status_code, 403)
        dados = json.loads(response.data)
        self.assertFalse(dados["sucesso"])
        self.assertIn("desativada", dados["erro"])

    def test_15_erro_rotas_padrao_flask(self):
        """Rotas inexistentes retornam 404 e métodos incorretos retornam 405 (Sem virar 500 no middleware)"""
        # Rota inexistente -> Deve retornar 404, não 500
        response = self.client.get("/rota-fantasma-inexistente")
        self.assertEqual(response.status_code, 404)

        # Método incorreto -> Deve retornar 405, não 500
        response = self.client.post("/produtos/1") # POST em rota de GET
        self.assertEqual(response.status_code, 405)

if __name__ == "__main__":
    unittest.main()
