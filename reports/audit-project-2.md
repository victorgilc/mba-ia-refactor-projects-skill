================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Credenciais Hardcoded
File: src/utils.js:1-7
Description: Credenciais de banco (dbUser/dbPass), chave do gateway de pagamento (`pk_live_...`) e credencial SMTP definidas literalmente no código-fonte.
Impact: Se o repositório vazar, qualquer pessoa tem acesso à infraestrutura de produção (banco, gateway, SMTP).
Recommendation: Mover para variáveis de ambiente via módulo de config (Padrão 1 do playbook) — `process.env.*`.

### [CRITICAL] Criptografia Caseira / Senha em Texto Puro
File: src/utils.js:17-23
Description: `badCrypto` implementa "hash" à mão com loop de 10000 repetições de base64 truncado; reversível e com altas colisões. O seed em `src/AppManager.js:11` grava senha `'123'` em texto puro.
Impact: Credenciais de usuários comprometíveis; quebra completa da confidencialidade de senhas.
Recommendation: Usar hash comprovado (scrypt/bcrypt/pbkdf2) e o seed deve inserir senhas JÁ hashadas (Padrão 4 do playbook).

### [CRITICAL] God Class / God Method
File: src/AppManager.js:25-138
Description: `setupRoutes` concentra roteamento, validação, regra de negócio, acesso a banco e decisão de pagamento num único handler com callbacks profundamente aninhados.
Impact: Impossível testar em isolamento; qualquer mudança afeta todo o fluxo; manutenção inviável.
Recommendation: Quebrar em models/controllers/services/routes por domínio (Padrão 3 do playbook).

### [HIGH] Lógica de Banco em Rota com N+1
File: src/AppManager.js:82-127
Description: O relatório financeiro dispara uma query por curso, por matrícula, por usuário e por pagamento dentro de loops aninhados (N+1), tudo dentro do route handler.
Impact: Gargalo severo de performance; acoplamento da rota ao banco.
Recommendation: Substituir por uma única query com JOIN num modelo dedicado e agregar no serviço (Padrões 6 e 8 do playbook).

### [HIGH] Estado Global Mutável
File: src/utils.js:9-10
Description: `globalCache` e `totalRevenue` são variáveis globais exportadas e mutadas pela aplicação sem encapsulamento.
Impact: Acoplamento oculto, dificuldade de teste e risco de corridas/estado inconsistente.
Recommendation: Encapsular em instância e injetar por dependência (Padrão 7 do playbook).

### [HIGH] Dados Sensíveis em Logs / Console
File: src/AppManager.js:45
Description: O checkout imprime o número do cartão e a chave do gateway de pagamento no console.
Impact: Vazamento de dados de cartão e segredos em logs; violação de PCI DSS.
Recommendation: Remover o log de dados sensíveis; nunca registrar cartão ou chaves (Padrão 1 do playbook).

### [HIGH] Contrato de Efeito Colateral — DELETE deixa órfãos
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` remove o usuário sem tratar matrículas/pagamentos relacionados e sem verificação de erro; resposta sempre 200.
Impact: Órfãos no banco e resposta que não reflete o estado real dos dados.
Recommendation: Preservar o efeito colateral original (sem cascata) OU atualizar a mensagem para descrever o comportamento real (Padrão 19 do playbook).

### [MEDIUM] Middleware/Autorização Ausente nas Rotas
File: src/AppManager.js:82, 131
Description: `/api/admin/financial-report` (admin) e `DELETE /api/users/:id` (destrutiva) não possuem qualquer checagem de autenticação/permissão.
Impact: Acesso não autorizado a relatórios financeiros e a deleção de usuários.
Recommendation: Middleware de auth/autorização central nas rotas sensíveis (Padrão 11 do playbook).

### [MEDIUM] Tratamento de Erro Vazio/Genérico sem Log
File: src/AppManager.js:41-136
Description: Erros de banco retornam mensagens genéricas (`"Erro DB"`, `"Erro Pagamento"`) sem log centralizado; DELETE ignora erro por completo (`res.send` direto).
Impact: Dificuldade de diagnóstico em produção; fuga de detalhes internos.
Recommendation: Centralizar no error handler com log no servidor e resposta genérica ao cliente (Padrão 10 do playbook).

### [MEDIUM] APIs Deprecated — Callback Hell com SQLite3
File: src/AppManager.js:1-138
Description: Uso de `sqlite3` com callbacks assíncronos gerando callback-hell profundo; padrão obsoleto na stack Node.
Impact: Dificuldade de manutenção, legibilidade ruim e risco de erros de concorrência.
Recommendation: Migrar para `node:sqlite`/`better-sqlite3` com API síncrona ou Promises (Padrão 15 do playbook).

### [LOW] Nomenclatura Ruim
File: src/AppManager.js:29-34
Description: Variáveis criptográficas `u`, `e`, `p`, `cid`, `cc` sem significado claro.
Impact: Legibilidade e manutenção comprometidas.
Recommendation: Renomear para nomes descritivos (`name`, `email`, `password`, `courseId`, `cardNumber`) (Padrão 14 do playbook).

### [LOW] Magic Numbers / Strings Mágicas
File: src/AppManager.js:46, 108; src/utils.js:19
Description: `"PAID"`/`"DENIED"` comparados como literais e o limite `10000` no loop de criptografia sem constante nomeada.
Impact: Legibilidade; troca de valor exige busca manual.
Recommendation: Extrair para constantes nomeadas (Padrão 13 do playbook).

================================
Total: 12 findings
================================
