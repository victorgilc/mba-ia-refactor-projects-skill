# ARCHITECTURE AUDIT REPORT

===============================
ARCHITECTURE AUDIT REPORT
===============================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (instalado 3.1.1) + Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code

## Contrato de API (inventário Fase 1)

| Método | URL | Status/código esperado |
|---|---|---|
| GET | `/` | 200 `{message, version}` |
| GET | `/health` | 200 `{status, timestamp}` |
| GET | `/tasks` | 200 lista (task + `overdue`, `user_name`, `category_name`) |
| GET | `/tasks/<id>` | 200 task; 404 `Task não encontrada` |
| POST | `/tasks` | 201 task; 400 `Dados inválidos`/`Título é obrigatório`/`Título muito curto`/`Título muito longo`/`Status inválido`/`Prioridade deve ser entre 1 e 5`/`Formato de data inválido. Use YYYY-MM-DD`; 404 `Usuário não encontrado`/`Categoria não encontrada` |
| PUT | `/tasks/<id>` | 200 task; 400 `Dados inválidos`/`Título muito curto`/`Título muito longo`/`Status inválido`/`Prioridade deve ser entre 1 e 5`/`Formato de data inválido`; 404 `Task não encontrada`/`Usuário não encontrado`/`Categoria não encontrada` |
| DELETE | `/tasks/<id>` | 200 `Task deletada com sucesso`; 404 `Task não encontrada` |
| GET | `/tasks/search?q&status&priority&user_id` | 200 lista (task.to_dict); bug: `int()` inválido → **500** |
| GET | `/tasks/stats` | 200 `{total,pending,in_progress,done,cancelled,overdue,completion_rate}` |
| GET | `/users` | 200 lista (user + `task_count`) |
| GET | `/users/<id>` | 200 user + `tasks`; 404 `Usuário não encontrado` |
| POST | `/users` | 201 user; 400 `Dados inválidos`/`Nome é obrigatório`/`Email é obrigatório`/`Senha é obrigatória`/`Email inválido`/`Senha deve ter no mínimo 4 caracteres`/`Role inválido`; 409 `Email já cadastrado` |
| PUT | `/users/<id>` | 200 user; 400 `Dados inválidos`/`Email inválido`/`Senha muito curta`/`Role inválido`; 404 `Usuário não encontrado`; 409 `Email já cadastrado` |
| DELETE | `/users/<id>` | 200 `Usuário deletado com sucesso` (deleta as tasks do usuário); 404 `Usuário não encontrado` |
| GET | `/users/<id>/tasks` | 200 lista (id,title,description,status,priority,created_at,due_date,overdue); 404 |
| POST | `/login` | 200 `{message, user, token}`; 400 `Dados inválidos`/`Email e senha são obrigatórios`; 401 `Credenciais inválidas`; 403 `Usuário inativo` |
| GET | `/reports/summary` | 200 relatório |
| GET | `/reports/user/<id>` | 200 relatório; 404 `Usuário não encontrado` |
| GET | `/categories` | 200 lista (categoria + `task_count`) |
| POST | `/categories` | 201 categoria; 400 `Dados inválidos`/`Nome é obrigatório` |
| PUT | `/categories/<id>` | 200 categoria; 404 `Categoria não encontrada` |
| DELETE | `/categories/<id>` | 200 `Categoria deletada`; 404 `Categoria não encontrada` |

## Summary
CRITICAL: 2 | HIGH: 5 | MEDIUM: 5 | LOW: 3

## Findings

### [CRITICAL] Senha com Hash Fraco (MD5) — Criptografia Caseira
File: models/user.py:27-32
Description: `set_password`/`check_password` usam `hashlib.md5()` para armazenar e comparar senhas (não é texto puro, mas MD5 é criptograficamente quebrado — brute-force/rainbow tables). `seed.py:19,26,33` insere senhas por esse caminho.
Impact: Comprometimento total de credenciais; ataque offline trivial sobre o banco.
Recommendation: Usar `werkzeug.security.generate_password_hash`/`check_password_hash` (scrypt, padrão moderno). O seed deve inserir senhas JÁ hashadas e, se houver banco legado com hash antigo, migrar/re-seed (Padrão 4).

### [CRITICAL] Credenciais Hardcoded
File: app.py:13 (SECRET_KEY 'super-secret-key-123') e services/notification_service.py:9-10 (email_user 'taskmanager@gmail.com', email_password 'senha123')
Description: Chave secreta e credenciais de SMTP gravadas em claro no código-fonte.
Impact: Exposição de segredos no repositório; acesso indevido se vazar.
Recommendation: Mover para variáveis de ambiente lidas em módulo de config (com `load_dotenv()` no topo), sem hardcoded (Padrão 1).

### [HIGH] Campo Sensível Serializado na Resposta (password/hash)
File: models/user.py:16-25 (to_dict inclui 'password'); exposto em routes/user_routes.py:33 (GET /users/<id>), :85 (POST /users 201), :129 (PUT /users 200), :209 (login)
Description: `User.to_dict()` retorna o hash da senha; toda resposta de usuário e login vaza o hash.
Impact: Vazamento de credenciais (mesmo hashado); vetor de brute-force offline.
Recommendation: DTO/whitelist com um único serializer público por entidade; nunca serializar `password` (Padrão 17).

### [HIGH] Token de Autenticação Falso / Login Sem Guard
File: routes/user_routes.py:210
Description: `/login` devolve `'token': 'fake-jwt-token-' + str(user.id)` — string previsível que NENHUMA rota valida. Nenhuma rota exige autenticação.
Impact: Falsa sensação de segurança; rotas destrutivas (DELETE/PUT) permanecem abertas.
Recommendation: Não devolver token falso — remover o campo e documentar a decisão de manter as rotas públicas como no original (sem quebrar o contrato), ou implementar guard real (Padrão 18 / AP-24).

### [HIGH] Lógica de Negócio dentro de Rotas (God Controller)
File: routes/task_routes.py:85-154, routes/user_routes.py:185-211, routes/report_routes.py:12-101
Description: As rotas concentram validação, regras de negócio (overdue, taxas, contagens), acesso a banco e formatação — misturando camadas em módulos de 200-300 linhas.
Impact: Forte acoplamento, difícil testar em isolamento, viola responsabilidade única.
Recommendation: Extrair orquestração para controllers e regras de negócio para services/use-cases; rotas apenas mapeiam URL → controller (Padrão 5).

### [HIGH] Camada de Dados Vazando nas Views/Routes
File: routes/task_routes.py:14,42,51; routes/user_routes.py:12,35,140; routes/report_routes.py:15-56,163
Description: SQLAlchemy (`Task.query`, `User.query`, `Category.query`) e `db` usados diretamente nos handlers das rotas, sem repositório/model intermediário.
Impact: Roteamento acoplado ao banco; quebra a separação MVC.
Recommendation: Banco acessado somente em models; controllers chamam a camada de dados (Padrão 6).

### [HIGH] Queries N+1 em Múltiplos Pontos de Leitura
File: routes/task_routes.py:42-57 (por task: `User.query.get` + `Category.query.get` → 2N queries); routes/user_routes.py:22 (`len(u.tasks)` por usuário → N); routes/report_routes.py:53-68 (por usuário: `Task.query.filter_by` → N); routes/report_routes.py:163 (`Task.query.filter_by(category_id=...).count()` por categoria → N)
Description: Quatro endpoints executam consultas em loop dentro de `for` sobre listas — N+1 clássico (ex.: listar 10 tasks = 21 queries).
Impact: Gargalo severo de performance conforme os dados crescem.
Recommendation: `joinedload` nas relações, `GROUP BY` agregado para contagens (task_count, user_stats) e eliminar query em loop em TODOS os pontos (Padrão 8 / 25).

### [MEDIUM] Tratamento de Erro Vazio/Broad + Ausência de Error Handler Central
File: routes/task_routes.py:62-63,151-154,236-238; routes/user_routes.py:130-132; routes/report_routes.py:186-188,221-223
Description: `except:` bare em vários handlers (engole exceção sem log) e não existe `@app.errorhandler`. Erro em `/tasks/search?priority=abc` estoura **500 HTML** (routes/task_routes.py:261).
Impact: Dificuldade de debug, respostas inconsistentes, 500 inesperados em input inválido.
Recommendation: Error handler centralizado que re-encaminha `HTTPException` (404/405/400 preservados) e retorna 5xx genérico apenas para erros internos, logando o detalhe (Padrão 10).

### [MEDIUM] Rotas Destrutivas Sem Autorização
File: routes/user_routes.py:134 (DELETE /users/<id>), routes/task_routes.py:225 (DELETE /tasks/<id>), routes/report_routes.py:211 (DELETE /categories/<id>)
Description: DELETE/PUT de recursos executam sem qualquer autenticação/autorização; o "login" devolve token que nada valida.
Impact: Acesso não autorizado a operações destrutivas.
Recommendation: A app legada não tinha auth real — não introduzir guard que quebre o contrato, mas remover o token falso (AP-24) e documentar a decisão de exposição das rotas (Padrão 18).

### [MEDIUM] Validação de Entrada Inconsistente / Input Mal Tratado → 500
File: routes/task_routes.py:261,264 (`int(priority)`/`int(user_id)` sem guard); routes/task_routes.py:113 (`priority < 1` quebra com string)
Description: `GET /tasks/search?priority=abc` e `?user_id=abc` geram **500** (ValueError) em vez de 400; validações manuais e duplicadas em cada rota (a própria `utils/helpers.py` tem validadores `process_task_data`/`validate_email` nunca usados).
Impact: Entradas malformadas quebram a API; comportamento inconsistente entre endpoints.
Recommendation: Validar/casting com tratamento de erro (400 com mensagem original) e centralizar validadores reutilizáveis (Padrão 12).

### [MEDIUM] APIs Deprecated — Flag Obsoleta SQLALCHEMY_TRACK_MODIFICATIONS
File: app.py:12
Description: `SQLALCHEMY_TRACK_MODIFICATIONS` é ignorada/obsoleta desde Flask-SQLAlchemy 3.x.
Impact: Código ancorado em API obsoleta; warnings; config enganosa.
Recommendation: Remover a flag junto com a migração (Padrão 15 / 23).

### [MEDIUM] Seed Destrutivo / Não Idempotente
File: seed.py:11-14
Description: `seed_data()` apaga TODAS as linhas de Task/User/Category e re-insere a cada execução — pressupõe banco vazio.
Impact: Executar seed sobrescreve dados pré-existentes; estado imprevisível.
Recommendation: Semear somente se o banco estiver vazio (idempotente), preservando dados existentes (Padrão 20).

### [LOW] Código Morto e Imports sem Chamador
File: routes/task_routes.py:7 (`json, os, sys, time` não usados); routes/user_routes.py:6 (`hashlib, json` não usados); routes/report_routes.py:8 (`json` e `format_date, calculate_percentage` importados e não usados); services/notification_service.py:1-48 (classe inteira sem chamador, além de credenciais hardcoded); utils/helpers.py:19-108 (validate_email, sanitize_string, generate_id, log_action, parse_date, is_valid_color, process_task_data sem chamadores)
Description: Imports, helpers e uma service inteira sem nenhuma chamada após leitura do código.
Impact: Ruído, manutenção custosa, leitores confundidos sobre o que é usado.
Recommendation: Remover código sem chamador; verificar com grep/rg antes de deletar (Padrão 24).

### [LOW] Nomenclatura Ruim / Variáveis Criptográficas
File: routes/report_routes.py:24-28 (`p1..p5`), routes/user_routes.py:14-23 (`u`), models/category.py:13 (`d`), models/task.py:45 (`p`)
Description: Nomes curtos e enganosos em trechos com lógica importante.
Impact: Legibilidade prejudicada.
Recommendation: Renomear para nomes descritivos (Padrão 14).

### [LOW] Magic Numbers / Constantes Soltas Duplicadas
File: routes/task_routes.py:39,110,177 (`['pending','in_progress','done','cancelled']`); routes/user_routes.py:71,120 (`['user','admin','manager']`); ranges 1-5 e 200/3 literais
Description: Listas de status/roles e limites repetidos literalmente em vários arquivos, apesar de `utils/helpers.py:110-116` já definir constantes (`VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`) que não são usadas.
Impact: Duplicação; mudança de regra exige editar vários lugares.
Recommendation: Constantes nomeadas e compartilhadas (Padrão 13).

===============================
Total: 15 findings
===============================

## Anti-patterns do catálogo consultados
AP-01, AP-04, AP-05, AP-06, AP-08, AP-11, AP-14, AP-15, AP-16, AP-17, AP-18, AP-20, AP-22, AP-24, AP-26, AP-27 (16 catálogos)

## Decisões de refatoração planejadas (Fase 3)
1. **Config extraída** (`config/settings.py`): `SECRET_KEY`, `DATABASE_PATH` via env com `load_dotenv()` no topo; remoção do segredo hardcoded e da flag `SQLALCHEMY_TRACK_MODIFICATIONS`.
2. **Senha**: migrar para `werkzeug.security` (scrypt). O banco legado (`tasks.db`) já possui hashes scrypt compatíveis — login preservado contra dados existentes. Seed passa a inserir hashes werkzeug.
3. **DTO/whitelist**: `to_dict()` público por entidade (sem `password`); único serializer por entidade (DRY).
4. **N+1**: `joinedload(Task.user/category)`, contagens com `GROUP BY` (task_count, user_stats, categories), overdue via query filtrada.
5. **Token falso**: removido do `/login` (AP-24) — decisão documentada; rotas permanecem públicas como no original (sem quebrar contrato).
6. **Error handler centralizado** com re-raise de `HTTPException` (404/405/400 preservados) + 400 para inputs inválidos que hoje estouram 500.
7. **Controllers** extraídos das rotas; rotas viram mapeamento fino (MVC); regras de negócio (overdue, stats, validações) delegadas a services/models.
8. **Código morto** removido (imports não usados, `notification_service.py` sem chamador, helpers órfãos) e **seed idempotente**.
