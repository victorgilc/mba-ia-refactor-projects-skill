# Catálogo de Anti-Patterns

Use na **Fase 2** para cruzar o código contra sinais concretos de detecção. Classificação de severidade segue a escala do curso: CRITICAL, HIGH, MEDIUM, LOW.

## Escala de Severidade

- **CRITICAL:** falha grave de arquitetura/segurança que impede funcionamento, expõe dados sensíveis ou viola totalmente a separação de responsabilidades.
- **HIGH:** forte violação de MVC/SOLID que dificulta muito manutenção e testes.
- **MEDIUM:** padronização, duplicação ou gargalos moderados.
- **LOW:** legibilidade, nomenclatura, magic numbers.

---

## AP-01 — Credenciais Hardcoded (CRITICAL)
**Sinal:** chaves secretas, senhas, tokens, API keys escritos literalmente no código.
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```js
const config = { paymentGatewayKey: "pk_live_1234567890abcdef", dbPassword: "senha_prod_123" };
```
```java
// application.properties
spring.datasource.password=minha-senha-123
```
```go
var dbPassword = "minha-senha-123"
```
```php
$secret = 'sk_live_1234567890abcdef';
```
```ruby
ENV = nil; DB_PASSWORD = "minha-senha-123"
```
**Impacto:** exposição de segredos; se vazado no repo, acesso indevido.
**Recomendação:** mover para variáveis de ambiente / módulo de config (env vars / `.env` / config server).

## AP-02 — SQL Injection (CRITICAL)
**Sinal:** montagem de query por concatenação de string com dados do usuário.
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT ... WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
```js
`Insert into users ... values ('${usr}', '${pwd}')`
```
```java
stmt = conn.createStatement();
stmt.execute("SELECT * FROM users WHERE email='" + email + "'");
```
```go
db.Query("SELECT * FROM users WHERE email='" + email + "'")
```
```php
$pdo->query("SELECT * FROM users WHERE email = '".$_POST['email']."'");
```
```ruby
User.where("email = '#{params[:email]}'")
```
**Impacto:** injeção de SQL, comprometimento completo do banco.
**Recomendação:** queries parametrizadas/placeholders — Python (`?`, `%s`, `:param`), JS (`?`/`$1`), Java (`PreparedStatement`), Go (`?` no `database/sql`), PHP (`PDO` bindValue), Ruby (ActiveRecord binds/`?`).

## AP-03 — God Class / God Method (CRITICAL)
**Sinal:** um único arquivo/função concentra de banco + negócio + validação + formatação de vários domínios; threads de responsabilidades variadas.
**Impacto:** impossível testar isoladamente; qualquer mudança afeta tudo.
**Recomendação:** separar em models/controllers por domínio.

## AP-04 — Senha em Texto Puro / Criptografia Caseira (CRITICAL)
**Sinal:** senha gravada diretamente; hash implementado à mão com loops de concatenação.
```js
function badCrypto(p){ let h=""; for(...) h += Buffer.from(p).toString('base64').substring(0,2); return h.substring(0,10);}
```
```java
String hash = Integer.toHexString(pwd.hashCode()); // cripto caseira
```
```go
func badHash(p string) string { return sha1.Sum([]byte(p + "salt"))[:8] } // fraco
```
**Impacto:** comprometimento de credenciais.
**Recomendação:** usar lib padrão e comprovada — `bcrypt`/`pbkdf2`/`argon2` (Python `werkzeug.security`/`bcrypt`, Node `bcrypt`/`argon2`, Java `BCrypt`/`PBKDF2`, Go `golang.org/x/crypto/bcrypt`, Ruby `bcrypt`, PHP `password_hash`); nunca reimplementar cripto.

## AP-05 — Lógica de Negócio dentro de Controller (HIGH)
**Sinal:** controller/rota contém regras complexas (cálculo de total, descontos, notificações, regras de status), sem delegar a services/use-cases.
**Impacto:** forte acoplamento, difícil testar.
**Recomendação:** extrair para camada de serviço/use-case; controller só orquestra.
**Sinal 2 (efeito colateral no fluxo HTTP):** dentro do handler que cria pedido / muda status há chamadas de efeito colateral — `print("ENVIANDO EMAIL/SMS/PUSH...")`, envio de e-mail, push, log duplicado de negócio — intercaladas com a resposta HTTP. Comunicação externa (e-mail/SMS/push) DEVE viver num `notification_service`/disparador próprio e o controller apenas o invoca (`service.notify(...)`), nunca imprimir/enviar no meio da construção da resposta. Ver Padrão 8 do playbook.

## AP-06 — Camada de Dados vazando em Views/Controllers (HIGH — viola MVC)
**Sinal:** SQL/`db` usado diretamente no route handler em vez de model/repositório.
**Impacto:** UI/roteamento acoplado ao banco; quebrar separação de responsabilidades.
**Recomendação:** criar models/repositories; controllers chamam camada de dados.

## AP-07 — Estado Global Mutável (HIGH)
**Sinal:** variáveis globais modular-level mutadas por toda a app.
```js
let globalCache = {};
function logAndCache(k, d){ globalCache[k] = d; }
```
```python
db_connection = None
```
**Impacto:** acoplamento oculto, dificuldade de teste, corridas.
**Recomendação:** injeção de dependência; encapsular em instância/classe.

## AP-08 — Lógica de Banco em Rota/Controller com N+1 (HIGH)
**Sinal:** loops que disparam query nova para cada item (N+1).
```js
courses.forEach(c => { this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], ...); });
```
```java
for (Course c : courses) { jdbc.query("SELECT * FROM enrollments WHERE course_id=" + c.getId()); }
```
```ruby
@courses.each { |c| Enrollment.where(course_id: c.id) } # N+1 via ActiveRecord
```
**Impacto:** gargalo de performance severo.
**Recomendação:** JOIN / carga em lote; mover para repositório. (Ver AP-13.)

## AP-09 — Endpoint Administrativo SQL Cru (CRITICAL/HIGH)
**Sinal:** rota admin que executa query arbitrária enviada pelo cliente.
```python
@app.route("/admin/query", methods=["POST"]) ... cursor.execute(query)
```
```java
@PostMapping("/admin/query") void run(@RequestBody String sql) { stmt.execute(sql); }
```
```go
func runQuery(w, r){ q := r.FormValue("sql"); db.Query(q) }
```
**Impacto:** qualquer requisição executa qualquer SQL → tomada de controle total.
**Recomendação:** remover ou restringir; nunca aceitar SQL de input.

## AP-10 — Resposta vazando Segredos/Stack Trace (HIGH)
**Sinal:** retorna config, `secret_key`, caminhos do DB, `expressão de erro` crua ao cliente.
```python
"secret_key": "minha-chave-super-secreta-123", "db_path": "loja.db", "debug": True
```
**Impacto:** exposição de infraestrutura e segredos.
**Recomendação:** remover segredos da resposta; logar erro, retornar mensagem genérica.

## AP-11 — Tratamento de Erro Vazio/Exposição (MEDIUM)
**Sinal:** `try/except: pass`, `except: return jsonify({'error': str(e)}), 500` expondo detalhes, ou `except:` sem especificar; equivalente em outras stacks (`catch(e){ res.json({error:e.message}) }`, `return fmt.Errorf(...)` exposto, `respond_to` com exceção crua).
**Impacto:** hard to debug, fuga de informação.
**Recomendação:** centralizar no error handler; logar e responder genericamente.

> **AP-11b (regressão comum):** error handler de `Exception` que NÃO re-encaminha `HTTPException`. Em Flask, `register_error_handler(Exception, ...)` pega o `NotFound`/`MethodNotAllowed`; sem `isinstance(e, HTTPException): re-raise/mantém o status`, rota inexistente vira **500** em vez de **404** e método errado vira **500** em vez de **405**. O mesmo vale em Express (verificar `err.status`/`err.statusCode`) e em qualquer framework que intercepte erros genéricos. Detectar e corrigir.

## AP-12 — Duplicação de Código (MEDIUM)
**Sinal:** bloco quase idêntico repetido (ex: criação de dict de produto repetido em várias funções; build de pedido duplicado).
```python
def get_todos_pedidos(): ... # idêntico a get_pedidos_usuario
```
**Impacto:** manutenção custosa, inconsistências.
**Recomendação:** extrair função/mixin/repository e reutilizar.

## AP-13 — Queries N+1 (MEDIUM)
**Sinal:** SELECT dentro de loop sobre resultados anteriores (já citado em AP-08; use quando não houver acoplamento forte).
**Recomendação:** JOIN/aggregação em lote.

## AP-14 — Middleware/Autorização Ausente nas Rotas (MEDIUM)
**Sinal:** rotas sensíveis (admin, delete, relatórios financeiros) sem checagem de autenticação/permissão; `app.use` incompleto.
```js
app.get('/api/admin/financial-report', (req,res) => { ... }); // sem auth
```
```go
r.GET("/admin/report", handler) // sem middleware de auth
```
```java
@GetMapping("/admin/report") // sem @PreAuthorize / SecurityFilterChain
```
**Impacto:** acesso não autorizado.
**Recomendação:** middleware de auth/autorização central (Express `app.use`, Go middleware, Java `@PreAuthorize`/filter, Django middleware, Rails `before_action`).

## AP-15 — Validação Inconsistente nas Rotas (MEDIUM)
**Sinal:** validações feitas manualmente e de forma diferente em cada endpoint; tipos não validados.
**Impacto:** entradas malformadas, bugs.
**Recomendação:** validadores reutilizáveis / schema (Pydantic, Joi, etc.).

## AP-16 — Magic Numbers / Constantes Soltas (LOW)
**Sinal:** números literais sem nome (0.1, 0.05, 0.02; limite `1000`, `5000`, `10000`; `0..9` em cripto).
**Impacto:** legibilidade.
**Recomendação:** constantes nomeadas / config.

## AP-17 — Nomenclatura Ruim / Variáveis Criptográficas (LOW)
**Sinal:** nomes como `u`, `e`, `p`, `cid`, `cc`, `dados`, `result`.
**Sinal 2:** função chamada `health` porém sem `_` separando (health_check) ou nomes enganosos.
**Recomendação:** nomes descritivos.

## AP-18 — APIs Deprecated (MEDIUM)
**Sinal:** uso de APIs obsoletas, removidas em versões novas do framework/lib.
**Exemplos (detecte por framework):**
- Flask: `before_first_request` (removido no Flask 2.3+); usar `app.before_request` ou bloco `with app.app_context()`.
- SQLAlchemy: `SQLALCHEMY_TRACK_MODIFICATIONS` (obsoleto); `Base.query`; `db.session.query(Model)` → `Model.query`.
- Express: callbacks/callback-hell com SQLite3 → migrar para Promises/async-await (`sqlite3` → `better-sqlite3`/`node:sqlite`); `app.del` etc.
- Node: `crypto.createHash` deprecated options; `Buffer` usa fortemente.
- Java/Spring: `WebSecurityConfigurerAdapter` (removido no Spring Security 5.7+/6); `@EnableWebSecurity` bean-based. `javax.*` → `jakarta.*` no Boot 3.
- Go: `io/ioutil` (deprecated no Go 1.16+) → `io.ReadAll`/`os.ReadFile`; `sqlmock`/drivers antigos.
- PHP: `mysql_*` (removido); `password_hash` em vez de `md5`/`sha1`. `date('Y-m-d', strtotime(...))` legado (não deprecated, mas frágil).
- Ruby: Rails 6→7 — `before_filter` → `before_action`; `uniq` → `uniq`/`distinct`; `ActiveRecord` `.first`/`.last` ok, mas `update_attributes` → `update`.
- C#/.NET: `.NET Core 2.x`/3.x → .NET 6+ — `AddRazorPages`/`IApplicationBuilder.UseMvc` deprecated; `Newtonsoft` → `System.Text.Json` no ASP.NET Core 3+.
**Recomendação:** identificar e recomendar o equivalente moderno daquela versão.

## AP-19 — Contrato de API Quebrado na Refatoração (HIGH) — auto-verificação na Fase 3
**Sinal:** após a refatoração, parte dos endpoints originais deixou de existir (ex: rotas de CRUD, busca/filtros, listagens, autenticação, relatórios, health, admin ou a rota-raiz foram omitidas no novo roteamento — só uma fração do que o original expunha foi reconquistado). Também inclui validações perdidas (campos obrigatórios que agora geram 500 por `KeyError`) e códigos de status alterados.
**Impacto:** consumidores da API (frontends, integrações) quebram silenciosamente.
**Recomendação:** conferir 1-a-1 a lista de endpoints + métodos + status registrada na Fase 1 contra o roteamento novo; usar o checklist de paridade (SKILL.md, Fase 3), genérico de stack. Se a app legada habilitava CORS, manter o middleware CORS equivalente.
**Sinal 2 (login):** seed/banco com senha em texto puro enquanto o novo login usa hash → usuários existentes não autenticam. Verificar migração de hash.

## AP-20 — Campo Sensível Serializado na Resposta (senha/hash/token) (HIGH)
**Sinal:** o modelo/entidade é serializado "inteiro" para a resposta — incluindo o campo de senha (hash) e/ou `token`, `cvv`, `numero_cartao`. Mesmo que a senha seja um **hash seguro**, expô-lo viola a confidencialidade e é um vetor de ataque (permite brute-force offline / roubo generalizado).
```python
def _usuario_to_dict(u):
    return {"id": u.id, "nome": u.nome, "email": u.email, "senha": u.senha}  # ⚠ hash vazado
```
```js
res.json({ ...user, password: user.passHash }); // ⚠ hash/token vazado
```
```java
// entity serializada inteira: inclui passwordHash
```
```go
// struct sem tag `json:"-"` no campo Hash/PasswordHash → vaza no JSON
```
**Impacto:** exposição de credenciais mesmo com hash; vazamento para listas, buscas, logins e logs.
**Recomendação (agnóstica — vale p/ TODA stack):** a resposta deve usar **DTO/whitelist** com apenas os campos públicos; nunca devolver a entidade inteira sem um ponto de mapeamento. Como resolver em cada stack: Python → funções de "dict público"; Node/Express → `const { senha, token, ...} = user; res.json(...)` ou `pick`/`omit`; Java → `UsuarioDTO`/`@JsonIgnore` nos campos sensíveis; Go → tag `json:"-"` ou `ToDTO()`; Rails → `as_json(only: [...])`/views; Laravel → `makeHidden`/Resource. Os **logs** também não podem registrar hash/senha. Fonte de transformação: **Padrão 17** do playbook.

## AP-21 — Comportamento de Efeito Colateral Alterado (Behavioral Drift) (HIGH)
**Sinal (Fase 3 / validação):** na refatoração, um endpoint mutador (create/update/delete) passa a ter efeito colateral DIFFERENTE do original no store **sem** que isso seja o contrato desejado — e, frequentemente, com a mensagem de resposta ainda descrevendo o comportamento antigo. Ex.: um `DELETE` que originalmente deixava registros órfãos passou a remover filhos em cascata, enquanto a resposta continua dizendo "os registros relacionados permanecem no banco". O código faz X e a mensagem/fastro de resposta diz Y.
**Impacto:** consumidores que dependem do efeito colateral ou do texto se comportam de forma inesperada; regressão silenciosa parecida com over-engineering disfarçado de melhoria.
**Recomendação (agnóstica, qualquer stack):** manter o efeito colateral exatamente como no original. Se a mudança for realmente necessária (ex.: limpeza em cascata), atualize a mensagem de resposta para descrever o novo comportamento. Comportamento e texto nunca podem se contradizer. Detectar comparando o que a query/rota legada fazia com o que a nova faz (ler o código antigo, não só o novo). Ver Padrão 19.

## AP-22 — Modelo de Persistência Alterado / Seed Não Idempotente (MEDIUM)
**Sinal:** o refactor trocou a fonte de dados de forma silenciosa (ex.: banco em memória `:memory:` → arquivo em disco, ou vice-versa), mudando o ciclo de vida dos dados — dados agora persistem entre execuções (leitura de relatórios/listagens muda), OU o seed re-insere/deduplica dados em cada boot porque pressupõe banco vazio.
**Impacto:** estado imprevisível, seed que sobrescreve/corrompe dados pré-existentes, respostas (relatórios, listagens) que variam conforme execuções anteriores.
**Recomendação (agnóstico):** preservar a fonte de dados original. Se for trocar, torne o **seed idempotente** (semear somente se vazio) e valide a paridade CONTRA os dados pré-existentes (não apague o banco antigo na validação). Ver Padrão 20.

## AP-23 — Config Lida no Momento Errado / `.env` Carregado Tarde (MEDIUM)
**Sinal:** o módulo de config lê variáveis de ambiente (`os.environ.get(...)`, `process.env.X`) **no momento do import**, mas o carregamento do `.env`/dotenv do framework só acontece mais tarde (ex.: dentro de `app.run()`/CLI boot em Flask, ou no entry point em Node). Como o config é importado antes, ele lê valores **vazios/defaults** — o `.env` é **silenciosamente ignorado** e a app roda com configuração errada sem erro aparente.
```python
# config.py — lido na importação, ANTES de o load_dotenv() do app.run() rodar
SECRET_KEY = os.environ.get("SECRET_KEY", "")
```
```js
// config.js — lido na importação, antes de require('dotenv').config() no entry point
module.exports = { secret: process.env.SECRET_KEY };
```
**Impacto:** segredos/caminho de banco/debug configurados via `.env` não são aplicados; a app roda com defaults vazios/inseguros sem sinalizar.
**Recomendação (agnóstico):** chamar explicitamente o loader de `.env` no **topo do módulo de config** (`from dotenv import load_dotenv; load_dotenv()` no Python; `require('dotenv').config()` no Node; leitura de `.env` equivalente em qualquer stack) ANTES de ler qualquer variável — nunca depender de o framework carregar depois. Ver Padrão 22.

## AP-24 — Token de Autenticação Falso / Login Sem Guard (MEDIUM)
**Sinal:** o endpoint de login retorna um "token" que **não é válido nem validado** (string fixa ou previsível, ex.: `"token-" + id`, `"fake-token"`) e NENHUMA rota valida esse token — o login existe mas não protege nada. Sinal 2: rotas mutadoras/destrutivas (`DELETE`, `PUT`, admin) permanecem abertas sem autenticação/autorização.
```js
// login retorna token falso que nenhuma rota valida
res.json({ token: "fake-token-" + user.id });   // mesmo caso em qualquer stack
```
**Impacto:** falsa sensação de segurança; acesso não autorizado a operações destrutivas.
**Recomendação (agnóstico):** se a app legada não tinha auth real, NÃO inventar um token falso que minta sobre proteção — ou implementar guard real (JWT/session/middleware de auth aplicado nas rotas) ou desativar/proteger as rotas destrutivas (403 "desabilitado") e **documentar a decisão** no relatório (AP-14 / Padrões 11 e 18).

## AP-25 — Config/Flags Deprecated Mantidas Após Migração (LOW)
**Sinal:** após migrar APIs deprecated (AP-18), a configuração obsoleta correspondente continua presente (ex.: `SQLALCHEMY_TRACK_MODIFICATIONS` definida em `app.config`/`config` depois que a lib passou a ignorá-la; opções deprecated em `config.js`/`application.properties`).
**Impacto:** código ancorado em APIs obsoletas; warnings; manutenção futura confusa.
**Recomendação (agnóstico):** ao migrar uma API deprecated, remover **também a flag/opção de config** correspondente, não só o uso no código. Ver Padrão 23.

## AP-26 — Código Morto Deixado pela Refatoração (LOW)
**Sinal:** após extrair para services/controllers, sobram imports, helpers, constantes e funções **sem nenhum chamador** (ex.: um validador/formatador que as rotas antigas usavam e ninguém mais chama; imports de bibliotecas que nenhum caminho usa; funções de utilidades que viraram órfãs).
**Impacto:** ruído, manutenção custosa, leitores confusos sobre o que é realmente usado.
**Recomendação (agnóstico):** no final da Fase 3, varrer com grep/rg cada função, constante e import — remover os que não têm chamador (ou rodar linter de código não usado: `eslint --no-unused-vars`, `ruff`/`flake8`, `tsc --noUnusedLocals`, `golangci-lint`, equivalente por stack). Ver Padrão 24.

## AP-27 — N+1 / Query em Loop Não Eliminado em TODOS os Pontos (HIGH)
**Sinal:** a refatoração otimizou o caso mais visível (ex.: a listagem principal com `JOIN`/`joinedload`) mas **outros endpoints seguem com query em loop** — detalhe de um recurso que carrega os filhos, listagem que conta registros relacionados por item, relatórios com agregação por entidade dentro de `for`/`forEach` (N+1 remanescente em detalhe, contagens e relatórios).
```js
// detalhe/relatório: 1 query por item dentro do loop
const items = await listAll();
for (const item of items) {
  const children = await db.query("SELECT * FROM child WHERE parent_id = ?", [item.id]);
}
```
**Impacto:** gargalo severo de performance que permanece após o "refactor" — problema de auditoria não resolvido.
**Recomendação (agnóstico):** varrer TODOS os pontos de leitura (listagem, detalhe, contagem, relatórios, stats) e aplicar JOIN/joinedload/agregação em lote em cada um, não só no endpoint principal. Ver Padrão 8/25.

---

## Checklist mínimo de cobertura
- [ ] Pelo menos 8 anti-patterns do catálogo são consultados.
- [ ] Distinção entre CRITICAL, HIGH, MEDIUM, LOW.
- [ ] Camada de APIs deprecated incluída (AP-18).
- [ ] Como detectar: cruze cada arquivo com os sinais ACIMA, anotando `File:linha`.