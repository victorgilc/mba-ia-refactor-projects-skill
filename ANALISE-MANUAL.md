# Análise Manual dos Projetos

Análise feita por leitura do código dos três projetos antes de automatizar a auditoria. Comentários organizados por arquivo, com a referência de linhas de cada achado.

---

## code-smells-project (Python/Flask, E-commerce)

Projeto monolítico em 4 arquivos. O `models.py` concentra a lógica de 4 domínios.

### app.py

`/admin/query` (`app.py:59-78`) executa SQL arbitrário enviado pelo cliente; `/admin/reset-db` (`app.py:47-57`) apaga o banco. Sem autenticação. SECRET_KEY hardcoded em `app.py:7`.

### controllers.py

`/health` (`controllers.py:276-290`) retorna `secret_key`, `db_path` e `debug: True` na resposta. `controllers.py:208-210` e `controllers.py:247-250` simulam notificação (email/SMS/push) com `print` dentro do fluxo HTTP. Mistura de idiomas/nomenclatura: campos `sucesso/erro` junto de mensagens em português e strings em inglês no print de notificação.

### models.py

Queries montadas por concatenação de strings em `models.py:28`, `models.py:47-49`, `models.py:110` e `models.py:289-297`. O `login_usuario` (linha 110) interpola email e senha direto na query. `models.py:1-314` mistura SQL, regra de negócio e serialização de 4 domínios no mesmo arquivo. `models.py:171-233` faz uma query extra por pedido e por item (N+1). Duplicação de serialização: `models.py:12-21`, `models.py:31-40` e `models.py:304-313` repetem o mesmo dicionário em vários pontos. Faixas de desconto `10000/5000/1000` e taxas `0.1/0.05/0.02` soltas em `models.py:256-262`.

### database.py

`database.py:76-79` grava senhas como `admin123` em texto puro no seed.

---

## ecommerce-api-legacy (Node.js/Express, LMS)

Checkout, rotas, regra de negócio, acesso a banco e pagamento concentrados em callbacks aninhados dentro do `AppManager.js`.

### src/utils.js

`utils.js:1-7` tem credenciais de banco, chave de gateway (`pk_live_...`) e SMTP fixos no código. `utils.js:17-23` (`badCrypto`) gera um "hash" a partir de base64 repetido e truncado, com colisões e reversível. `utils.js:9-10` (`globalCache`, `totalRevenue`) exportados e alterados sem controle.

### src/AppManager.js

`AppManager.js:45` imprime o número do cartão no console. `AppManager.js:25-138` (`setupRoutes`) concentra roteamento, validação, banco e decisão de pagamento em callbacks profundos. `AppManager.js:7` usa `:memory:`, perdendo os dados a cada restart (problema num fluxo de checkout). `AppManager.js:131-137` remove o usuário sem limpar as matrículas e os pagamentos, deixando órfãos. `AppManager.js:29-34` usa nomes de variáveis pouco descritivos (`u`, `e`, `p`, `cid`, `cc`). `"PAID"/"DENIED"` comparados como string mágica em `AppManager.js:46` e `AppManager.js:108`.

---

## task-manager-api (Python/Flask, Task Manager)

Já possui separação em `models/`, `routes/`, `services/`, `utils/`, mas a lógica de negócio continua nos routes.

### models/user.py

`models/user.py:29-32` usa MD5 para senha; `models/user.py:21` (`to_dict`) inclui o campo `password` na resposta.

### models/task.py

`models/task.py:50-60` repete a regra de overdue que também existe em `routes/task_routes.py:30-39`, `routes/user_routes.py:171-180` e `routes/report_routes.py:34-43`. Uma cópia (`get_task`) nem checa status.

### routes/user_routes.py

`routes/user_routes.py:207-211` devolve token `'fake-jwt-token-...'` e nenhuma rota valida auth. Mínimo de senha em `routes/user_routes.py:64`; `MIN_PASSWORD_LENGTH` existe no helpers mas não é usado.

### routes/task_routes.py

`routes/task_routes.py` reimplementa validações que já existem em `helpers.process_task_data` (`helpers.py:57-108`); `routes/task_routes.py:7` importa `json, os, sys, time` sem uso. `routes/task_routes.py:62` usa `except` sem tipo, engolindo o erro sem log. Limites de prioridade 1-5 soltos em `routes/task_routes.py:113`.

### routes/report_routes.py

Queries por usuário em `routes/report_routes.py:53-68` e count por categoria em `routes/report_routes.py:157-165` (N+1). `routes/report_routes.py:186` usa `except` sem tipo, engolindo o erro sem log.

### services/notification_service.py

`services/notification_service.py:8-10` tem credencial de email fixa no código.

### utils/helpers.py

`utils/helpers.py` importa `os, json, sys, math, hashlib` sem uso.