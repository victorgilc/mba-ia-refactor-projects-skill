================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~660 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:28, 47-50, 109-111, 289-299
Description: Queries montadas por concatenação de string com dado do usuário em praticamente todas as funções de acesso a dados — `get_produto_por_id`, `criar_produto`, `login_usuario` (`WHERE email = '...' AND senha = '...'`) e `buscar_produtos` (query dinâmica com `LIKE '%'+termo+'%'`).
Impact: Um request controlado pode injetar SQL e ler/modificar/apagar todo o banco (produtos, pedidos, usuários).
Recommendation: Substituir por queries parametrizadas com placeholder `?` em TODAS as consultas (`cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))`) (Padrão 2 do playbook).

### [CRITICAL] Credenciais Hardcoded
File: app.py:7; controllers.py:289; database.py:5
Description: `SECRET_KEY` definida em claro (`'minha-chave-super-secreta-123'`), `db_path = "loja.db"` fixo e, pior, o `/health` devolve a `secret_key`, o `db_path` e `debug=True` na resposta pública.
Impact: Exposição de segredo e de detalhes de infraestrutura; compromete sessões e dados se o repo vazar.
Recommendation: Mover para variável de ambiente via módulo de config (Padrão 1 do playbook) e remover segredos da resposta de health (Padrão 17).

### [CRITICAL] Endpoint Administrativo SQL Cru
File: app.py:59-78
Description: `/admin/query` executa qualquer SQL enviado pelo cliente no corpo da requisição, sem autenticação.
Impact: Qualquer chamador executa SQL arbitrário no banco de produção → tomada de controle total.
Recommendation: Remover a rota (ou restringir a uma whitelist de queries parametrizadas internas); nunca executar SQL vindo do cliente (Padrão 9 do playbook).

### [CRITICAL] Senha em Texto Puro
File: models.py:126-129; database.py:75-83
Description: `criar_usuario` grava `senha` exatamente como recebida e o seed insere usuários com senhas em claro (`admin123`, `123456`, `senha123`); o login compara senha em texto puro na query (models.py:109-111).
Impact: Comprometimento total de credenciais; vazamento do banco expõe todas as senhas.
Recommendation: Hash seguro (`werkzeug.security.generate_password_hash`/`check_password_hash`) e seed com senhas JÁ hashadas (Padrão 4 do playbook).

### [HIGH] God Class / God Method
File: controllers.py:1-292; models.py:1-314
Description: `controllers.py` concentra todos os handlers de 4 domínios (produtos, usuários, pedidos, relatórios) com validação, regra de negócio e efeitos colaterais; `models.py` concentra todo o acesso a dados e a regra de desconto.
Impact: Impossível testar em isolamento; qualquer mudança afeta todo o fluxo; manutenção inviável.
Recommendation: Quebrar em models/controllers por domínio (Padrão 3 do playbook) e extrair regra de desconto/notificação para service (Padrão 5).

### [HIGH] Lógica de Banco com N+1
File: models.py:139-166, 171-233
Description: `criar_pedido` dispara query por item em loop; `get_pedidos_usuario` e `get_todos_pedidos` aninham cursores (`cursor2`/`cursor3`) para buscar itens e nomes de produtos por pedido (N+1).
Impact: Gargalo severo de performance; acoplamento da camada de dados à iteração manual.
Recommendation: Substituir por queries com JOIN / carga em lote num repositório (Padrões 6 e 8 do playbook).

### [HIGH] Resposta vazando Segredos/Stack Trace
File: controllers.py:285-290, 10-12
Description: `/health` retorna `secret_key`, `db_path` e `debug` no corpo da resposta; vários handlers retornam `str(e)` da exceção crua ao cliente (`{"erro": str(e)}`).
Impact: Exposição de infraestrutura e segredos; fuga de detalhes internos.
Recommendation: Remover segredos da resposta; logar no servidor e retornar mensagem genérica (Padrões 1 e 10 do playbook).

### [HIGH] Campo Sensível Serializado na Resposta (senha)
File: models.py:83, 99; controllers.py:132, 144
Description: `get_todos_usuarios`/`get_usuario_por_id` incluem o campo `senha` no dict, e os controllers `listar_usuarios`/`buscar_usuario` devolvem isso ao cliente sem whitelist.
Impact: Senhas (em texto puro) vazam em listagens e buscas de usuários.
Recommendation: Usar DTO/whitelist — nunca serializar `senha`; um único serializer de campos públicos por entidade (Padrão 17 do playbook).

### [MEDIUM] Tratamento de Erro Vazio/Genérico sem Log
File: controllers.py:10-12, 21-22, 60-62, 108-109, 185-186
Description: `try/except` repetido em cada handler retornando `{"erro": str(e)}` com 500, sem log centralizado no servidor.
Impact: Dificuldade de diagnóstico em produção e fuga de detalhes internos.
Recommendation: Centralizar no error handler com `app.logger.exception` e resposta genérica, preservando status HTTP legítimos (404/405/400) (Padrão 10 do playbook).

### [MEDIUM] Middleware/Autorização Ausente nas Rotas
File: app.py:47-57, 59-78
Description: `/admin/reset-db` (apaga todo o banco) e `/admin/query` (SQL arbitrário) não possuem qualquer checagem de autenticação/permissão.
Impact: Acesso não autorizado a operações destrutivas e a execução de SQL.
Recommendation: Middleware de auth/autorização central nas rotas sensíveis; proteger/desativar rotas destrutivas (Padrões 11 e 18 do playbook).

### [MEDIUM] Duplicação de Código
File: models.py:171-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` são praticamente idênticos (mesma construção de pedido com itens), e o dict de produto é remontado em 3 funções.
Impact: Manutenção custosa e inconsistências entre cópias.
Recommendation: Extrair funções de mapeamento/repositório reutilizadas (DRY) (Padrões 12 e 17 do playbook).

### [LOW] Magic Numbers / Constantes Soltas
File: models.py:256-262
Description: Faixas de desconto `10000`, `5000`, `1000` com percentuais `0.1`, `0.05`, `0.02` literalmente no código de `relatorio_vendas`.
Impact: Legibilidade; troca de valor exige busca manual.
Recommendation: Extrair para constantes nomeadas/config (Padrão 13 do playbook).

### [LOW] Nomenclatura Ruim
File: models.py:187-192, 219-224; controllers.py:26, 37-41
Description: Cursores `cursor2`/`cursor3` e variáveis genéricas `dados`/`result` sem significado claro.
Impact: Legibilidade e manutenção comprometidas.
Recommendation: Renomear para nomes descritivos (Padrão 14 do playbook).

================================
Total: 13 findings
================================
