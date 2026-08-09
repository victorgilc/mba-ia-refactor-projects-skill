# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

---

## Documentação do Desafio

Esta seção documenta o processo completo: análise manual, construção da skill, resultados da execução e como reproduzir tudo. A ferramenta escolhida foi o **Gemini CLI**, então a skill está em `.gemini/skills/refactor-arch/` (o conceito e a estrutura interna são idênticos aos do Claude Code).

### A) Análise Manual

Análise feita por leitura direta do código dos três projetos **antes** de automatizar a auditoria (ver `ANALISE-MANUAL.md`). Cada projeto tem no mínimo 5 problemas, com pelo menos 1 CRITICAL/HIGH, 2 MEDIUM e 2 LOW, com justificativa de relevância.

#### Projeto 1 — code-smells-project (Python/Flask, E-commerce)

Projeto monolítico em 4 arquivos; o `models.py` concentra a lógica de 4 domínios (produtos, usuários, pedidos, relatórios).

| Severidade | Problema | Localização | Por que é relevante |
|---|---|---|---|
| CRITICAL | SQL Injection por concatenação de strings | `models.py:28, 47-49, 110, 289-297` | Queries montadas com `f"...'{email}'..."` e `LIKE '%'+termo+'%'` permitem que um request controlado leia/modifique/apague o banco inteiro. |
| CRITICAL | Segredos hardcoded e vazados no `/health` | `app.py:7`, `controllers.py:276-290` | `SECRET_KEY` fixa em claro; `/health` devolve `secret_key`, `db_path` e `debug: True` na resposta pública — exposição de infraestrutura e de sessões. |
| CRITICAL | Endpoint `/admin/query` executa SQL cru sem auth | `app.py:59-78` | Qualquer chamador executa SQL arbitrário; junto com `/admin/reset-db` (`app.py:47-57`), dá tomada de controle total. |
| CRITICAL | Senhas em texto puro | `database.py:76-79`, `models.py:109-111` | Seed grava `admin123` em claro e o login compara texto puro dentro da query; vazamento do banco expõe todas as credenciais. |
| HIGH | God Class / God Method | `models.py:1-314`, `controllers.py` | Um único arquivo concentra SQL, regra de negócio, serialização e handlers de 4 domínios; impossível testar em isolamento. |
| HIGH | N+1 em pedidos | `models.py:171-233` | Query por pedido e por item em loops aninhados (`cursor2`/`cursor3`); gargalo severo conforme os dados crescem. |
| HIGH | Campo `senha` serializado na resposta | `models.py:83, 99`, `controllers.py:132, 144` | Listagens e buscas de usuários devolvem a senha (em texto puro) ao cliente. |
| MEDIUM | Tratamento de erro genérico sem log | `controllers.py:10-12, 21-22, 60-62, 108-109, 185-186` | `try/except` repetido em cada handler devolvendo `{"erro": str(e)}` com 500; dificulta diagnóstico e vaza detalhes internos. |
| MEDIUM | Rotas administrativas sem autorização | `app.py:47-78` | `/admin/reset-db` (apaga o banco) e `/admin/query` (SQL cru) sem qualquer checagem de permissão. |
| MEDIUM | Duplicação de código/serialização | `models.py:12-21, 31-40, 304-313` | O mesmo dict de produto/usuário é remontado em várias funções; manutenção custosa e cópias divergentes. |
| LOW | Magic numbers | `models.py:256-262` | Faixas de desconto `10000/5000/1000` e taxas `0.1/0.05/0.02` soltas no código de `relatorio_vendas`. |
| LOW | Nomenclatura ruim e mistura de idiomas | `models.py:187-192, 219-224`, `controllers.py` | Cursores `cursor2`/`cursor3`, variáveis `dados`/`result` sem significado; campos `sucesso/erro` misturados com prints em inglês. |

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS)

Checkout, rotas, regra de negócio, banco e pagamento concentrados em callbacks aninhados dentro do `AppManager.js`.

| Severidade | Problema | Localização | Por que é relevante |
|---|---|---|---|
| CRITICAL | Credenciais hardcoded | `src/utils.js:1-7` | Credenciais de banco, chave do gateway (`pk_live_...`) e SMTP fixas no código-fonte; vazamento do repo expõe toda a infraestrutura. |
| CRITICAL | Criptografia caseira (`badCrypto`) | `src/utils.js:17-23` | "Hash" à mão com base64 repetido/truncado — reversível e com colisões; o seed grava senha `'123'` em texto puro. |
| HIGH | God Class / God Method | `src/AppManager.js:25-138` | `setupRoutes` concentra roteamento, validação, banco e decisão de pagamento em callbacks profundos; acoplamento total. |
| HIGH | Lógica de banco em rota com N+1 | `src/AppManager.js:82-127` | Relatório financeiro dispara query por curso, matrícula, usuário e pagamento em loops aninhados. |
| HIGH | Estado global mutável | `src/utils.js:9-10` | `globalCache` e `totalRevenue` exportados e mutados sem encapsulamento; dificulta teste e cria corridas. |
| HIGH | Dados sensíveis em log | `src/AppManager.js:45` | Checkout imprime o número do cartão e a chave do gateway no console — violação de PCI DSS. |
| HIGH | DELETE deixa órfãos | `src/AppManager.js:131-137` | Remove o usuário sem limpar matrículas/pagamentos; resposta 200 que não reflete o estado real do banco. |
| MEDIUM | Rotas sensíveis sem autorização | `src/AppManager.js:82, 131` | `/api/admin/financial-report` e `DELETE /api/users/:id` sem auth; acesso a relatórios financeiros e deleção. |
| MEDIUM | Erros genéricos sem log | `src/AppManager.js:41-136` | `"Erro DB"`/`"Erro Pagamento"` sem log centralizado; DELETE ignora erro por completo. |
| MEDIUM | APIs deprecated — callback hell | `src/AppManager.js:1-138` | `sqlite3` com callbacks assíncronos gera callback-hell profundo; padrão obsoleto na stack Node. |
| LOW | Nomenclatura criptográfica | `src/AppManager.js:29-34` | Variáveis `u`, `e`, `p`, `cid`, `cc` sem significado. |
| LOW | Strings mágicas | `src/AppManager.js:46, 108`, `src/utils.js:19` | `"PAID"`/`"DENIED"` e o limite `10000` do loop de criptografia sem constante nomeada. |

#### Projeto 3 — task-manager-api (Python/Flask, Task Manager)

Já possui separação em `models/`, `routes/`, `services/`, `utils/`, mas a lógica de negócio continua presa nas rotas.

| Severidade | Problema | Localização | Por que é relevante |
|---|---|---|---|
| CRITICAL | Hash de senha fraco (MD5) | `models/user.py:27-32` | `hashlib.md5()` para armazenar/comparar senhas — criptograficamente quebrado, brute-force/rainbow tables triviais. |
| CRITICAL | Credenciais hardcoded | `app.py:13`, `services/notification_service.py:9-10` | `SECRET_KEY 'super-secret-key-123'` e credenciais SMTP (`taskmanager@gmail.com`/`senha123`) em claro no código. |
| HIGH | Campo `password`/hash serializado | `models/user.py:21`, `routes/user_routes.py` | `to_dict()` devolve o hash; toda resposta de usuário e login vaza o hash (vetor de brute-force offline). |
| HIGH | Token de autenticação falso | `routes/user_routes.py:207-211` | `/login` devolve `'fake-jwt-token-<id>'` previsível que nenhuma rota valida; rotas destrutivas permanecem abertas. |
| HIGH | Lógica de negócio dentro das rotas | `routes/task_routes.py`, `routes/report_routes.py` | Rotas concentram validação, regra de overdue, contagens e acesso a banco em módulos de 200-300 linhas (God Controller). |
| HIGH | N+1 em múltiplos pontos | `routes/task_routes.py:42-57`, `routes/report_routes.py:53-68, 163` | Query em loop por task/usuário/categoria; listar 10 tasks vira ~21 queries. |
| MEDIUM | Error handling ausente → 500 em input inválido | `routes/task_routes.py:261, 264` | `GET /tasks/search?priority=abc` estoura **500** (ValueError) em vez de 400; `except:` bare em vários handlers. |
| MEDIUM | Rotas destrutivas sem autorização | `routes/user_routes.py:134`, `routes/task_routes.py:225`, `routes/report_routes.py:211` | DELETE/PUT de recursos executam sem auth; o "login" devolve token que nada valida. |
| MEDIUM | Validação duplicada e helpers órfãos | `routes/task_routes.py`, `utils/helpers.py:57-108` | Validações reimplementadas nas rotas apesar de `process_task_data`/`validate_email` existirem sem uso. |
| MEDIUM | Flag deprecated | `app.py:12` | `SQLALCHEMY_TRACK_MODIFICATIONS` obsoleta desde Flask-SQLAlchemy 3.x. |
| MEDIUM | Seed destrutivo | `seed.py:11-14` | Apaga todas as linhas e re-insere a cada execução; execução sobrescreve dados pré-existentes. |
| LOW | Código morto / imports sem chamador | `routes/task_routes.py:7`, `services/notification_service.py`, `utils/helpers.py` | `json, os, sys, time` não usados; service de notificação e helpers inteiros sem chamadores. |
| LOW | Nomenclatura ruim | `routes/report_routes.py:24-28`, `models/task.py:45` | `p1..p5`, `u`, `d`, `p` sem significado em trechos com lógica importante. |
| LOW | Magic numbers / constantes duplicadas | `routes/task_routes.py:39, 110, 177` | Listas de status/roles e limites repetidos literalmente, apesar de constantes definidas em `utils/helpers.py`. |

### B) Construção da Skill

#### Decisões de design do SKILL.md

- **3 fases sequenciais e obrigatórias** (Análise → Auditoria → Refatoração), com ordem fixa documentada no topo do prompt para o agente nunca pular fases.
- **Fase 2 com confirmação obrigatória**: a skill **pausa e pergunta** `Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [y/n]` antes de qualquer modificação. O relatório é salvo em `../reports/audit-project-N.md` **mesmo que a Fase 3 seja negada** — ele é um entregável independente.
- **Contrato de API na Fase 1**: o agente inventaria todas as rotas (método + URL + status esperado) e usa essa tabela como lista de verificação de paridade na Fase 3 — cada rota do contrato precisa reaparecer na app nova.
- **Tabela "Fonte de conhecimento"**: o SKILL.md diz quando ler cada arquivo de referência (Fase 1 → `project-analysis.md`, Fase 2 → `antipattern-catalog.md` + `report-template.md`, Fase 3 → `mvc-guidelines.md` + `refactoring-playbook.md`), em vez de despejar todo o conhecimento no prompt.
- **Regras de paridade explícitas** (adicionadas após a 2ª iteração, ver desafios): preservar efeitos colaterais de create/update/delete (DELETE com órfãos continua órfão, **ou** a mensagem é atualizada para descrever o comportamento novo — código e mensagem nunca podem se contradizer); preservar o modelo de persistência (memória vs. arquivo) ou tornar o seed idempotente; não devolver token de autenticação falso; carregar `.env` no topo do config; remover flags deprecated junto com a API migrada.

#### Estrutura dos arquivos de referência

| Arquivo | Conteúdo |
|---|---|
| `project-analysis.md` | Heurísticas para detectar linguagem, framework, DB e mapear arquitetura; lista de arquivos/pastas a ignorar (`node_modules`, `__pycache__`, `*.db`). |
| `antipattern-catalog.md` | **27 anti-patterns (AP-01 a AP-27)** com sinais de detecção, severidade (CRITICAL→LOW) e referência cruzada com os padrões do playbook. Inclui detecção de APIs deprecated (AP-18) e padrões "escapadiços" (token falso AP-24, `.env` tarde AP-23, flag deprecated AP-25, código morto AP-26, N+1 residual AP-27). |
| `report-template.md` | Formato padronizado do relatório: cabeçalho (project, stack, files), Summary com contagem por severidade, Findings com `[Severidade] Nome`, `File:linhas`, `Description`, `Impact`, `Recommendation`, e total ao final. |
| `mvc-guidelines.md` | Regras do padrão MVC alvo: responsabilidades de cada camada (config, models, views/routes, controllers, middlewares/error handler, entry point), SOLID/KISS/DRY. |
| `refactoring-playbook.md` | **25 padrões de transformação (Padrão 1 a 25)** com exemplos de código antes/depois e o anti-pattern que cada um resolve. |

#### Por que os anti-patterns escolhidos

O catálogo (27 itens) cobre os problemas reais encontrados na análise manual dos 3 projetos:

- **CRITICAL:** credenciais hardcoded (AP-01), SQL Injection (AP-02), God Class (AP-03), senha em texto puro/criptografia caseira (AP-04), endpoint administrativo SQL cru (AP-09).
- **HIGH:** lógica de negócio em controller (AP-05), camada de dados vazando nas rotas (AP-06), estado global mutável (AP-07), N+1 em rota (AP-08), resposta vazando segredos (AP-10), contrato quebrado (AP-19), campo sensível serializado (AP-20), drift comportamental (AP-21), N+1 residual (AP-27).
- **MEDIUM:** erro vazio/exposição (AP-11), duplicação (AP-12), N+1 (AP-13), auth ausente (AP-14), validação inconsistente (AP-15), APIs deprecated (AP-18), seed não idempotente (AP-22), `.env` carregado tarde (AP-23), token falso (AP-24).
- **LOW:** magic numbers (AP-16), nomenclatura (AP-17), flag deprecated (AP-25), código morto (AP-26).

#### Como a skill é agnóstica de tecnologia

- As regras são descritas em termos de **padrões** (ex.: "query SQL montada por concatenação de string com dado do usuário"), não de sintaxe específica. Os exemplos do playbook mostram a transformação em Python/Flask **e** em Node/Express.
- A Fase 1 detecta stack antes de qualquer auditoria; a Fase 3 usa a estrutura MVC genérica (config / models / views-routes / controllers / middlewares), que existe em qualquer stack.
- Validação da Fase 3 é feita por **requisições HTTP reais** (não por API específica de framework), comparando status contra o contrato da Fase 1 — funciona igual para Flask e Express.
- O mesmo SKILL.md e as mesmas referências foram copiados nos 3 projetos sem nenhuma alteração específica de projeto.

#### Desafios encontrados e como resolvi

1. **1ª iteração (projeto 1):** a Fase 3 corrigiu os anti-patterns mas o relatório inicial não tinha arquivo/linha exatos em todos os findings → adicionada regra obrigatória "cada finding com `arquivo` e `linhas` exatas" e validação do template.
2. **Regressão de login pós-refatoração:** trocar senha em texto puro por hash quebrou o login dos usuários do banco antigo → adicionada regra de **migração de dados** (re-hash do que está no banco) e seed com senhas já hashadas (Padrão 4).
3. **Contrato de API parcial:** na 1ª execução, a Fase 3 "esqueceu" rotas auxiliares e alguns handlers devolveram status diferentes do original → adicionada a obrigação de **inventariar o contrato completo na Fase 1** e conferir rota a rota na Fase 3 (Padrão 16).
4. **Efeito colateral do DELETE:** o projeto 2 deletava usuário deixando órfãos; uma refatoração "melhorada" que introduziu cascade mudou o comportamento observável → adicionada a regra de **paridade de efeitos colaterais**: preservar o comportamento original (DELETE continua deixando órfãos, com a mensagem descrevendo isso) ou atualizar a mensagem para refletir o novo comportamento (Padrão 19).
5. **Token falso / auth:** o projeto 3 devolvia `fake-jwt-token-...` sem nenhum guard → decisão documentada: **remover o token falso** (o `/login` agora retorna só `message` + `user`) e manter as rotas públicas como no legado, sem introduzir guard que quebrasse o contrato (Padrão 11/18; AP-24).
6. **Persistência em memória vs. arquivo:** o projeto 2 usa `:memory:` (perde dados a cada restart); preservar esse comportamento original era parte do contrato → mantido `:memory:` e o seed idempotente (Padrão 20).

### C) Resultados

#### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|
| 1 — code-smells-project | 4 | 4 | 3 | 2 | 13 | `reports/audit-project-1.md` |
| 2 — ecommerce-api-legacy | 3 | 4 | 3 | 2 | 12 | `reports/audit-project-2.md` |
| 3 — task-manager-api | 2 | 5 | 5 | 3 | 15 | `reports/audit-project-3.md` |

Todos os projetos atingiram os critérios de aceite: Fase 1 detectou a stack corretamente (3/3), Fase 2 encontrou ≥ 5 findings com ≥ 1 CRITICAL/HIGH (3/3), e a aplicação continua funcionando após a refatoração (3/3).

#### Antes × Depois da estrutura

**Projeto 1 — code-smells-project**

```
ANTES (monolito, 4 arquivos)          DEPOIS (MVC)
code-smells-project/                  code-smells-project/
├── app.py                            ├── app.py                  (entry point / composition root)
├── controllers.py                    ├── src/config/settings.py  (env + fallback hardcoded — ver nota do checklist)
├── models.py                         ├── src/models/             (database, produto, usuario, pedido)
├── database.py                       ├── src/controllers/        (produto, usuario, pedido, relatorio)
└── requirements.txt                  ├── src/services/           (notificacao)
                                      ├── src/views/routes.py     (roteamento fino)
                                      ├── src/middlewares/error_handler.py (re-raise HTTPException)
                                      ├── test_app.py             (15 testes de paridade)
                                      └── requirements.txt
```

**Projeto 2 — ecommerce-api-legacy**

```
ANTES (3 arquivos)                    DEPOIS (MVC)
ecommerce-api-legacy/                 ecommerce-api-legacy/
├── src/AppManager.js                 ├── src/app.js              (entry point)
├── src/utils.js                      ├── src/config/index.js     (process.env)
└── src/app.js                        ├── src/models/             (user, course, enrollment, payment, report, auditLog, database)
                                      ├── src/controllers/        (checkout, report, user)
                                      ├── src/services/           (checkout, payment, report)
                                      ├── src/routes/             (checkout, report, user)
                                      ├── src/middlewares/errorHandler.js
                                      └── src/utils/crypto.js     (scrypt)
```

**Projeto 3 — task-manager-api**

```
ANTES (camadas parciais, negócio nas rotas)   DEPOIS (MVC completo)
task-manager-api/                             task-manager-api/
├── app.py                                    ├── app.py              (entry point + error handler)
├── routes/*.py (God Controller)              ├── config.py           (env + load_dotenv no topo)
├── models/*.py                               ├── controllers/        (task, user, report, category)
├── services/notification_service.py          ├── services/           (task, user, report, category)
└── utils/helpers.py                          ├── routes/             (blueprints finos → controllers)
                                              ├── models/             (task, user, category)
                                              ├── middlewares/error_handler.py (re-raise HTTPException)
                                              ├── seed.py             (idempotente, hashes werkzeug)
                                              └── utils/helpers.py
```

#### Checklist de validação preenchido

Aplicado o mesmo template a cada projeto, marcado fielmente contra o código real:

**Projeto 1 — code-smells-project**

```
### Fase 1 — Análise
- [x] Linguagem detectada corretamente  (Python)
- [x] Framework detectado corretamente  (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente  (E-commerce API — produtos, pedidos, usuários)
- [x] Número de arquivos analisados condiz com a realidade  (4 arquivos, ~660 LOC)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados  (13 findings)
- [x] Detecção de APIs deprecated incluída (se aplicável)  (N/A — nenhuma API deprecated em uso no legado)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC  (src/{config,models,controllers,views,services,middlewares})
- [ ] Configuração extraída para módulo de config (sem hardcoded)  — PARCIAL: extraída para src/config/settings.py, mas settings.py:3 mantém fallback hardcoded da SECRET_KEY ("minha-chave-super-secreta-123") e settings.py:5 o default "loja.db"
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado  (src/middlewares/error_handler.py re-encaminha HTTPException → 404/405 preservados)
- [x] Entry point claro  (app.py)
- [x] Aplicação inicia sem erros  (python -m unittest test_app -v → 15/15 OK)
- [x] Endpoints originais respondem corretamente  (ver logs/validation-project-1.txt)
```

**Projeto 2 — ecommerce-api-legacy**

```
### Fase 1 — Análise
- [x] Linguagem detectada corretamente  (JavaScript/Node.js)
- [x] Framework detectado corretamente  (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente  (LMS — cursos, matrículas, checkout, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade  (3 arquivos, ~180 LOC)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados  (12 findings)
- [x] Detecção de APIs deprecated incluída (se aplicável)  (AP-18 — callback hell com sqlite3)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC  (src/{config,models,controllers,services,routes,middlewares,utils})
- [x] Configuração extraída para módulo de config (sem hardcoded)  (src/config/index.js via process.env.*)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado  (src/middlewares/errorHandler.js)
- [x] Entry point claro  (src/app.js)
- [x] Aplicação inicia sem erros  (boot na porta 3000 — logs/server-project-2.out)
- [x] Endpoints originais respondem corretamente  (ver logs/validation-project-2.txt)
```

**Projeto 3 — task-manager-api**

```
### Fase 1 — Análise
- [x] Linguagem detectada corretamente  (Python)
- [x] Framework detectado corretamente  (Flask 3.0.0 / 3.1.1)
- [x] Domínio da aplicação descrito corretamente  (Task Manager — tarefas, usuários, categorias, relatórios)
- [x] Número de arquivos analisados condiz com a realidade  (15 arquivos, ~1158 LOC)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados  (15 findings)
- [x] Detecção de APIs deprecated incluída (se aplicável)  (AP-25 — SQLALCHEMY_TRACK_MODIFICATIONS)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC  (controllers/, models/, routes/, services/, middlewares/)
- [x] Configuração extraída para módulo de config (sem hardcoded)  (config.py via env + load_dotenv no topo; SECRET_KEY sem valor fixo)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento  (blueprints finos)
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado  (middlewares/error_handler.py re-encaminha HTTPException → 404/405 preservados)
- [x] Entry point claro  (app.py → create_app())
- [x] Aplicação inicia sem erros  (boot na porta 5000)
- [x] Endpoints originais respondem corretamente  (ver logs/validation-project-3.txt)
```

#### Logs de validação (aplicações rodando após a refatoração)

- `logs/validation-project-1.txt` — suíte de paridade do projeto 1: `Ran 15 tests in 12s — OK` (15/15).
- `logs/server-project-2.out` — boot do servidor Express: `Frankenstein LMS rodando na porta 3000...`
- `logs/validation-project-2.txt` — requisições HTTP reais no projeto 2: checkout aprovado (card 4111 → 200), checkout recusado (card 5111 → 400), relatório financeiro (200), DELETE de usuário mantendo a mensagem legada de órfãos (200), rota inexistente (404).
- `logs/validation-project-3.txt` — boot do Flask na porta 5000 + sequência de chamadas HTTP: raiz/health (200), listagem e detalhe de tasks (200), busca com `priority=abc` e `user_id=abc` agora retornam **400** (antes estouravam 500), stats (200), users sem password na resposta (200), criação de task (201), login sem token falso (200), login com senha errada (401), reports summary (200), categories (200), rota inexistente (404), método errado (405).

#### Observações sobre o comportamento da skill em stacks diferentes

- **Python/Flask (projetos 1 e 3):** mesmo com níveis de organização muito diferentes (monolito de 4 arquivos vs. camadas parciais), a skill identificou os mesmos anti-patterns de segurança e arquitetura (SQL injection, senha fraca, N+1, DTO) sem ajustes específicos.
- **Node/Express (projeto 2):** a mesma skill detectou callback hell com API deprecated (`sqlite3`), estado global mutável e criptografia caseira — padrões que não existiam nos projetos Python — provando a agnosticidade.
- **Preservação de contrato:** nos 3 projetos os endpoints originais continuaram respondendo com os mesmos status, e os erros de framework (404/405) foram preservados pelo error handler com re-raise de `HTTPException` — exceção feita ao caso documentado do projeto 2 (DELETE legado com órfãos) e à decisão do projeto 3 (remoção do token falso do `/login`).

### D) Como Executar

#### Pré-requisitos

- **Gemini CLI** instalada e configurada (a skill usa a convenção `.gemini/skills/`). Se preferir Claude Code ou Codex, adapte a pasta para `.claude/skills/` ou o equivalente — o `SKILL.md` e os arquivos de referência são os mesmos.
- Python 3.11+ com as dependências dos projetos (`requirements.txt` de cada projeto) e Node.js 22+ (usa `node:sqlite`, nativo).
- A pasta `.gemini/skills/refactor-arch/` já está copiada dentro dos 3 projetos.

#### Executar a skill em cada projeto

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
gemini   # invocar a skill refactor-arch

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
gemini   # invocar a skill refactor-arch

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
gemini   # invocar a skill refactor-arch
```

> A invocação varia conforme a ferramenta. No Claude Code: `claude "/refactor-arch"`. No Gemini CLI, a skill da pasta `.gemini/skills/` é carregada pelo nome `refactor-arch`.

A skill executa as 3 fases e, ao final da Fase 2, **pausa pedindo confirmação** antes de qualquer modificação. O relatório de auditoria é salvo em `../reports/audit-project-N.md`.

#### Validar que a refatoração funcionou

- **Projeto 1:** `python -m unittest test_app -v` — 15 testes de paridade devem passar (OK).
- **Projeto 2:** `npm start` (ou `node src/app.js`) e conferir o boot `Frankenstein LMS rodando na porta 3000...`; depois testar as rotas do contrato (`POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`, rota inexistente → 404).
- **Projeto 3:** `python app.py` (boot na porta 5000) e conferir os endpoints do contrato — inclusive `GET /tasks/search?priority=abc` → **400** (e não 500), `POST /tasks` → 201, `/login` sem token falso, rota inexistente → 404, método errado → 405.
- Os resultados capturados deste desafio estão em `logs/validation-project-{1,2,3}.txt`.

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.