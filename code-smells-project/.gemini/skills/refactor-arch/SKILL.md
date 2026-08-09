---
name: refactor-arch
description: Auditoria e refatoração arquitetural automatizada de codebases para o padrão MVC. Use this skill when the user asks to analyze, audit, "refactor-arch", refactor, restructure, fix the architecture, detect anti-patterns/code smells, generate an architecture audit report, or migrate a legacy codebase to MVC across any language/framework (Python/Flask, Node/Express, etc).
---

# refactor-arch — Auditoria e Refatoração para MVC

Você é um engenheiro sênior especialista em arquitetura de software (MVC, SOLID), segurança e refatoração. Este skill é **agnóstico de tecnologia** e executa uma refatoração incremental em **3 fases sequenciais e obrigatórias**, sempre pausando para confirmação humana antes de modificar qualquer arquivo.

## Sequência de Execução (não pule fases, não mude a ordem)

1. **FASE 1 — Análise:** detectar linguagem, framework, banco de dados, domínio e mapear a arquitetura atual.
2. **FASE 2 — Auditoria:** cruzar o código contra o catálogo de anti-patterns, gerar o relatório e **pedir confirmação** antes de prosseguir.
3. **FASE 3 — Refatoração:** reestruturar para MVC, validar que a app funciona (boot + endpoints).

## Fonte de conhecimento

Antes de executar, leia e use os arquivos de referência abaixo:

| Arquivo | Quando ler |
|---|---|
| `references/project-analysis.md` | Fase 1 — heurísticas p/ detectar stack, framework, DB e mapear arquitetura |
| `references/antipattern-catalog.md` | Fase 2 — sinais de detecção de anti-patterns + severidade |
| `references/report-template.md` | Fase 2 — formato padronizado do relatório |
| `references/mvc-guidelines.md` | Fase 3 — regras do padrão MVC alvo |
| `references/refactoring-playbook.md` | Fase 3 — padrões de transformação com antes/depois |

## FASE 1 — ANÁLISE DE PROJETO

Objetivo: entender o que é o projeto antes de criticá-lo.

Passos:
1. Enumere todos os arquivos-fonte do repositório (ignore `node_modules`, `.venv`, `.git`, `__pycache__`, `*.db`, pastas de dependências).
2. Use as heurísticas de `references/project-analysis.md` para detectar:
   - `Language` (ex: Python, JavaScript/Node.js)
   - `Framework` + versão (ex: Flask 3.1.1, Express 4.18.2)
   - `Dependencies` principais
   - `Domain` da aplicação (ex: E-commerce API — produtos, pedidos, usuários)
   - `Architecture` atual (ex: Monolítica, Parcialmente em camadas)
   - Banco de dados e tabelas
3. Conte o total de arquivos-fonte e de linhas de código.
4. **Inventarie o CONTRATO DE API (obrigatório):** registre TODA rota exposta pela app legada em uma tabela com 3 colunas — `Método` + `URL` + `Código/status esperado` — inclusive rotas auxiliares (`/`, `/health`, `/admin/...`). Para isso leia os entry points/roteamento (ex: `app.add_url_rule(...)`, `@app.route`, `Blueprint`, `app.use('/...')`, `router.get(...)`) e anote também o corpo/validações de cada handler (campos obrigatórios, mensagens de erro e status retornados como 400/401/404/500). **Este contrato será a lista de verificação de integridade que a Fase 3 deve reconquistar — nenhum endpoint ou comportamento pode ficar de fora.**
5. Imprima o resumo no formato EXATO abaixo.

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <lang>
Framework:     <framework versão>
Dependencies:  <deps>
Domain:        <descrição>
Architecture:  <arquitetura>
Source files:  <N> files analyzed
DB tables:     <lista, se aplicável>
================================
```

Não modifique nenhum arquivo nesta fase.

## FASE 2 — AUDITORIA ARQUITETURAL

Objetivo: encontrar e classificar anti-patterns com localização precisa.

Passos:
1. Leia cada arquivo-fonte e cruze-o contra `references/antipattern-catalog.md`.
2. Para cada achado registre: `[Severidade] Nome`, `File:linha`, `Description`, `Impact`, `Recommendation`.
3. Use `references/report-template.md` para montar o relatório.
4. **Requisitos mínimos:**
   - Pelo menos **8 anti-patterns distintos** consultados no catálogo.
   - Pelo menos **5 findings** detectados no projeto.
   - Pelo menos **1 CRITICAL ou HIGH**.
   - Todos ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW).
   - Cada finding com `arquivo` e `linhas` exatas.
   - Incluir detecção de **APIs deprecated** quando aplicável.
   - Apontar credenciais hardcoded e SQL Injection (CRITICAL).
   - **Atenção redobrada (pontos que costumam "escapar"):** token de autenticação falso em login (AP-24); `.env`/dotenv carregado tarde e config lendo env vars cedo demais (AP-23); config/flag deprecated mantida após migração (AP-25); código morto/imports sem chamador (AP-26); N+1 remanescente em detalhe/contagens/relatórios (AP-27).
5. Conte o total de findings.
6. **SALVAR o relatório em arquivo (obrigatório — não pule):** grave o relatório completo (exatamente o conteúdo montado no passo 3, com o formato do `references/report-template.md`) em `../reports/audit-project-N.md`, onde `N` é o número do projeto no repositório (projeto 1 = `code-smells-project`, projeto 2 = `ecommerce-api-legacy`, projeto 3 = `task-manager-api` — ex.: `code-smells-project` → `../reports/audit-project-1.md`, `ecommerce-api-legacy` → `../reports/audit-project-2.md`, `task-manager-api` → `../reports/audit-project-3.md`). Se a pasta `reports/` não existir na raiz do repositório, crie-a. **Este arquivo é um entregável obrigatório da auditoria e deve existir independentemente da confirmação da Fase 3.**

**IMPORTANTE — Confirmação obrigatória:** ao final da Fase 2, **PARE e pergunte ao usuário** antes de qualquer modificação:

```
Total: <N> findings
Relatório salvo em ../reports/audit-project-N.md
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [y/n]
```

Nunca inicie a Fase 3 sem uma resposta afirmativa (y/yes) do usuário.

## FASE 3 — REFATORAÇÃO PARA MVC

Objetivo: reestruturar o projeto seguindo `references/mvc-guidelines.md`, eliminando os anti-patterns da Fase 2 usando `references/refactoring-playbook.md`.

Passos:
1. Definir a estrutura MVC de destino (config, models, views/routes, controllers, middlewares/error handler, entry point) — veja `references/mvc-guidelines.md`.
2. Para cada anti-pattern encontrado, aplicar o padrão de transformação correspondente de `references/refactoring-playbook.md`.
3. **Sempre**:
   - Extrair configuração (secrets, chaves, debug, caminho do banco) para um módulo de config, sem hardcoded no código. Usar variáveis de ambiente.
   - Substituir concatenação de strings em SQL por **queries parametrizadas**.
   - Não armazenar senha em texto puro; usar hash seguro (ex: `bcrypt`, `pbkdf2`, `werkzeug.security`). Não reimplementar criptografia caseira.
   - **Hash com migração de dados (anti-regressão de login):** se o banco já existe com senhas em texto puro ou com hash antigo, aplicar migração/re-seed, ou o login quebra para usuários existentes. O seed da app refatorada DEVE inserir senhas JÁ hashadas — nunca texto puro. `check_password_hash`/`bcrypt.compare` só funciona se o que está no banco foi gerado pelo mesmo hash.
   - **Respostas com DTO/whitelist (não serializar segredos):** NENHUMA resposta (listar, buscar, detalhar, login) pode incluir o campo de senha/hash (`senha`/`password`) nem `token`/`cvv`/número de cartão. Cada entidade usa um **único serializer** de campos públicos (DRY) — mesmo que a senha esteja hashada, o hash não pode vazar.
   - Centralizar tratamento de erros em um middleware/error handler único (sem try/except vazios e sem expor stack traces ao cliente). **RE-RAISE de erros HTTP:** o handler deve dar `raise e` (ou re-encaminhar) para `HTTPException` (404, 405, 400 do próprio framework) e responder 5xx genérico SOMENTE para erros internos reais — caso contrário, rotas inexistentes e métodos errados viram 500 em vez de 404/405.
   - **Preservar o contrato de API INTEGRALMENTE:** registrar a MESMA lista de endpoints da Fase 1 (mesma rota + método). Confira rota por rota a tabela inventariada; não declare a Fase 3 completa com endpoints faltando.
   - **Preservar validações e códigos de status:** campos obrigatórios, regras (negativos, limites, categorias) e os status retornados (400/401/404/201/200) devem continuar idênticos ao original. Validação de entrada não pode ser descartada na refatoração.
   - **Preservar middlewares globais** que o original usava (ex: `CORS(app)`), para não quebrar consumidores cross-origin.
   - **Carregar `.env`/dotenv NO TOPO do config, antes de ler qualquer variável de ambiente.** Se o loader (ex: `load_dotenv()` no Python, `dotenv.config()` no Node) só roda depois (dentro de `app.run()`/boot do framework), o config importado antes fica com valores vazios e o `.env` é **silenciosamente ignorado** — segredos/caminho de banco/debug não são aplicados sem erro aparente (AP-23 / Padrão 22).
   - **Remover config/flags deprecated junto com a API migrada** — não basta trocar a chamada obsoleta; a opção de config correlata (ex: `SQLALCHEMY_TRACK_MODIFICATIONS`) também deve sair (AP-25 / Padrão 23).
   - **Não devolver token de autenticação falso** (string fixa/previsível como `"token-" + id`, `"fake-token"`) que nenhuma rota valida — ou implemente guard real aplicado às rotas, ou desative/proteja as rotas destrutivas (403 "desabilitado") e **documente a decisão no relatório** (AP-24 / Padrões 11 e 18).
   - **Eliminar N+1 em TODOS os pontos de leitura**, não só no endpoint principal: verifique também detalhe por id, listagens com contagem de registros relacionados, relatórios e stats — nenhum `SELECT`/`Query` dentro de `for` (AP-27 / Padrão 25).
   - **Remover código morto deixado pela refatoração:** imports, helpers, constantes e funções sem nenhum chamador (grep por nome; rodar linter de unused, ex: `ruff`/`flake8`/`eslint`) (AP-26 / Padrão 24).
   - **Aplicar os princípios SOLID, KISS e DRY** ao código refatorado (detalhes em `references/mvc-guidelines.md`): cada classe/módulo com uma única responsabilidade (S, OCP), sem depender de concretos internos (DIP), sem reimplementar criptografia/comportamento já existente (DRY), e sem over-engineering — a solução mais simples que preserva o contrato original (KISS). Refatorar para não adicionar complexidade desnecessária.
   - **NÃO alterar a semântica dos efeitos colaterais de endpoints mutadores (create/update/delete).** O *comportamento observável* (quais linhas são escritas/apagadas/atualizadas — ex.: um DELETE deixa órfãos ou remove em **cascata**) faz parte do contrato tanto quanto a rota e o status. Mantenha o efeito colateral original; se a melhoria for obrigatória (ex.: introduzir limpeza em cascata), **atualize a mensagem de resposta** para descrever o novo comportamento. Comportamento e mensagem NUNCA podem se contradizer — se o código faz X e a mensagem diz que faz Y, é regressão disfarçada de melhoria.
   - **Preservar o modelo de persistência/estado (banco em memória vs. arquivo/banco real).** Não troque a fonte de dados como efeito colateral da refatoração (ex.: `:memory:` para arquivo em disco). Isso muda o ciclo de vida dos dados (reset a cada execução vs. estado que persiste entre restarts) e altera respostas (ex.: relatórios) sem aviso. Se a troca for inevitável: torne o **seed idempotente (semear só se vazio)**, nunca assuma banco vazio no boot e valide a paridade CONTRA dados pré-existentes (não apague/apague o banco antigo na validação).
   - **Endpoints mutadores NÃO se valem apenas pela resposta HTTP 2xx.** Para delete/update/insert, verifique escritas no store (contagem/apogem das linhas efetivamente alteradas, limpeza de filhos/registros relacionados). "O endpoint respondeu 200" não prova que o comportamento foi preservado.
4. Regerar o roteamento e validar a paridade:
   - Registre no entry point/blueprint **todas** as rotas do contrato da Fase 1, exatamente com os mesmos métodos.
   - Teste HTTP real em **cada endpoint do contrato** (não só em alguns), conferindo o status esperado (inclusive 400/401/404).
   - Teste também **casos de erro**: rota inexistente deve retornar 404 (não 500), método errado deve retornar 405, validações devem retornar 400 com as mesmas mensagens.
   - Se o banco legado existir com dados antigos, valide o fluxo de login/leitura usando esses dados (não apague o banco na validação).
5. Imprimir ao final a nova estrutura de pastas e o resultado da validação.

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de pastas>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## VALIDAÇÃO DA FASE 3 (obrigatória)

Não declare a Fase 3 como completa sem validar **paridade TOTAL** com o contrato da Fase 1:
- **Python/Flask:** instalar deps e iniciar a app sem erros; executar requisições HTTP reais (ex: `curl`/`Invoke-WebRequest`/`test_client()`) em **TODOS os endpoints do contrato**, conferindo o status exato (não apenas "deu 2xx").
- **Node/Express:** `npm start` (ou `node src/app.js`) deve iniciar sem erros; testar **todas** as rotas com requisições.
- **Checklist obrigatório de paridade (repita manualmente antes de declarar sucesso):**
  - [ ] O inventário de endpoints da Fase 1 foi comparado 1-a-1 com as rotas da app nova (nenhuma rota/método faltando).
  - [ ] Cada GET/POST/PUT/DELETE responde com o status esperado.
  - [ ] Rota inexistente → 404 (nunca 500). Método errado → 405 (nunca 500).
  - [ ] Validações de entrada → 400 com as mesmas mensagens do original (sem virar 500 por KeyError).
  - [ ] Login funciona com os dados do banco legado existente (hash compatível com o armazenado).
  - [ ] Middlewares globais originais (ex: CORS) mantidos.
  - [ ] Respostas de erro não expõem stack trace nem segredos.
   - [ ] Efeitos colaterais de create/update/delete verificados NO STORE (linhas escritas/removidas — ex.: órfãos vs. cascade), não só pelo status HTTP.
   - [ ] Modelo de persistência preservado (memória vs. arquivo) ou, se trocado, seed idempotente e validação feita sobre dados pré-existentes.
   - [ ] Mensagens/tex de resposta originais preservados — ou coerentes com o comportamento novo (sem contradição entre código e texto retornado).
   - [ ] `.env`/dotenv carregado no topo do config ANTES de ler env vars — config não roda com valores vazios ignorados.
   - [ ] Config/flag deprecated removida junto com a API migrada (ex.: `SQLALCHEMY_TRACK_MODIFICATIONS`).
   - [ ] Nenhum token de autenticação falso retornado; decisão de auth/desativação de rotas destrutivas documentada no relatório.
   - [ ] N+1 eliminado em TODOS os pontos de leitura (detalhe, listagens com contagem, relatórios, stats), não só na listagem principal.
   - [ ] Código morto (imports, helpers, constantes sem chamador) removido.
   - [ ] SOLID respeitado (responsabilidade única por camada; sem god class; DIP/DI em vez de estado global).
   - [ ] DRY respeitado (validações/queries/respostas compartilhadas, não copiadas).
   - [ ] KISS respeitado (sem over-engineering; solução mais simples que mantém o contrato).
- Corrigir qualquer violação de paridade e repetir até a app iniciar sem erros e TODOS os endpoints responderem com o comportamento original.

## Contrato
- Trabalhe apenas dentro do diretório do projeto em execução, com uma única exceção: **o relatório de auditoria da Fase 2 DEVE ser salvo em `../reports/audit-project-N.md`** (na pasta `reports/` da raiz do repositório).
- Preserve o comportamento e os endpoints originais.
- Não altere `SKILL.md` nem os arquivos de referência da skill.
- Comunique cada decisão arquitetural de forma sucinta ao final.