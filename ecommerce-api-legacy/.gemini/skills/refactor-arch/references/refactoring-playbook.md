# Playbook de Refatoração — Padrões de Transformação

Use na **Fase 3**. Para cada anti-pattern da auditoria, aplique o padrão correspondente. Cada padrão tem exemplo antes/depois e deve ser adaptado à stack do projeto.

## Padrão 1 — Extrair Segredos para Config (AP-01, AP-10)
**Antes (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
**Depois:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "app.db")
```
**Antes (Node):**
```js
const config = { paymentGatewayKey: "pk_live_123...", dbPassword: "..." };
```
**Depois:**
```js
// config.js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPassword: process.env.DB_PASSWORD,
  port: process.env.PORT || 3000,
};
```
**Antes (Java):**
```java
// application.properties
spring.datasource.password=minha-senha-123
```
**Depois:**
```properties
spring.datasource.password=${DB_PASSWORD}
```
**Antes (Go):**
```go
var dbPassword = "minha-senha-123"
```
**Depois:**
```go
// config/config.go
func DatabasePassword() string { return os.Getenv("DB_PASSWORD") }
```
**Antes (Ruby):**
```ruby
DB_PASSWORD = "minha-senha-123"
```
**Depois:**
```ruby
DB_PASSWORD = ENV.fetch("DB_PASSWORD")
```
> Remover também segredos de respostas JSON e logs (health check nunca deve retornar `secret_key`/`db_path`/`debug`).

## Padrão 2 — Parametrizar Queries SQL (AP-02)
**Antes:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```
**Depois:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
**Antes (Node):**
```js
this.db.run(`INSERT INTO users ... VALUES ('${u}', '${e}', '${hash}')`)
```
**Depois:**
```js
this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [u, e, hash])
```
**Antes (Java):**
```java
Statement st = conn.createStatement();
st.execute("SELECT * FROM users WHERE email='" + email + "'");
```
**Depois:**
```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE email=?");
ps.setString(1, email);
```
**Antes (Go):**
```go
rows, _ := db.Query("SELECT * FROM users WHERE email='" + email + "'")
```
**Depois:**
```go
rows, _ := db.Query("SELECT * FROM users WHERE email=?", email)
```
**Antes (PHP):**
```php
$pdo->query("SELECT * FROM users WHERE email='" . $email . "'");
```
**Depois:**
```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$stmt->execute([$email]);
```
**Antes (Ruby):**
```ruby
User.where("email = '#{params[:email]}'")
```
**Depois:**
```ruby
User.where("email = ?", params[:email])
```
> Aplicar em TODA query que receba input do usuário (busca, login, filtros).

## Padrão 3 — Quebrar God Class em Models + Controllers (AP-03)
**Antes:** `models.py` com banco, regras de domínio e queries de 4 domínios em 350 linhas.
**Depois:**
```
models/produto_model.py    # consultas/CRUD de produtos (parametrizadas)
models/usuario_model.py    # consultas/CRUD + login
models/pedido_model.py     # pedidos, itens_pedido
controllers/produto_controller.py   # validação de entrada + orquestração
controllers/pedido_controller.py    # fluxo de criação de pedido
```
**Antes:** `AppManager.js` com roteamento + banco + pagamento + matrícula num único handler.
**Depois:** separar `controllers/checkoutController.js`, `models/`, `routes/checkoutRoutes.js`, `services/paymentService.js`.

> **Genérico:** em qualquer stack o padrão é o mesmo — extrair por responsabilidade (model de dados, rota, controller, service). Em Java: `ProdutoController` + `ProdutoService` + `ProdutoRepository`; em Go: `handlers.ProdutoHandler` + `services.ProdutoService` + `repositories.ProdutoRepo`; em Rails: `controllers/produtos_controller.rb` + `models/produto.rb` + `services/pedido_service.rb`; em Laravel: `Http/Controllers/ProdutoController.php` + `Models/Produto.php` + `Services/PedidoService.php`.

## Padrão 4 — Hash de Senha Seguro (AP-04)
**Antes (Node):**
```js
function badCrypto(pwd){ let h=""; for(...) h += Buffer.from(pwd).toString('base64').substring(0,2); return h.substring(0,10); }
```
**Depois (Node):**
```js
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 10);
const ok = await bcrypt.compare(password, user.pass);
```
**Depois (Python):**
```python
from werkzeug.security import generate_password_hash, check_password_hash
hash = generate_password_hash(senha)
check_password_hash(hash, senha)
```
**Depois (Java):**
```java
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
BCryptPasswordEncoder enc = new BCryptPasswordEncoder();
String hash = enc.encode(senha);
boolean ok = enc.matches(senha, user.getSenha());
```
**Depois (Go):**
```go
import "golang.org/x/crypto/bcrypt"
h, _ := bcrypt.GenerateFromPassword([]byte(senha), bcrypt.DefaultCost)
ok := bcrypt.CompareHashAndPassword(user.Hash, []byte(senha)) == nil
```
**Depois (PHP):**
```php
$hash = password_hash($senha, PASSWORD_BCRYPT);
$ok = password_verify($senha, $user['hash']);
```
**Depois (Ruby):**
```ruby
require 'bcrypt'
hash = BCrypt::Password.create(senha)
ok = BCrypt::Password.new(user.hash) == senha
```
> **Migração obrigatória (evita quebrar login):** a comparação SÓ funciona se o que está no banco foi gerado pelo mesmo hash da lib correspondente. Se o banco legado existe com senhas em texto puro (ou seed inserindo texto puro), o login do app refatorado falhará para todos. Ao refatorar: (a) o seed deve inserir JÁ o hash (função da lib daquela stack), e (b) migrar usuários existentes (update em lote rehaseando) ou re-seed. NUNCA comparar hash de entrada contra texto puro armazenado.

## Padrão 5 — Extrair Lógica de Negócio para Service (AP-05)
**Antes (Python — controller com regras):**
```python
def criar_pedido():
    ...
    if faturamento > 10000: desconto = faturamento * 0.1
    elif faturamento > 5000: desconto = faturamento * 0.05
```
**Depois (service/use-case):**
```python
# services/pedido_service.py
class PedidoService:
    def calcular_desconto(self, faturamento): ...
```
O controller passa a chamar `PedidoService().calcular_desconto(...)`.
**Depois (Node):** extrair regra de pagamento para `services/paymentService.js`; o route handler apenas chama o serviço e responde.
**Depois (Java):** `ProdutoService` com `@Service`; controller injeta o service (`@Autowired`/construtor) e chama o método.
**Depois (Go):** `services/pedido_service.go` com funções/struct; handler recebe o service via DI.
**Depois (Rails):** `app/services/pedido_service.rb` (`PedidoService.calcular_desconto(...)`); controller delega.
**Depois (Laravel):** `app/Services/PedidoService.php` injetado no controller (construtor/`app()`).

## Padrão 6 — Banco Somente em Models/Repositórios (AP-06)
**Antes (JS — SQL no route handler):**
```js
app.get('/api/admin/financial-report', (req, res) => {
  this.db.all("SELECT * FROM courses", [], ...);
});
```
**Depois:**
```js
// models/reportModel.js
async function getFinancialReport(db) { return await db.all("SELECT ... JOIN ..."); }
// routes/adminRoutes.js → controller reportController → model
```
**Depois (Python — Flask):** rotas em `views/routes.py` chamam controllers; controllers chamam models; nenhum `cursor.execute` em rota.
**Depois (genérico):** o mesmo vale em qualquer stack — banco apenas em models/repositories/DAOs; controller/handler nunca importa driver de DB. Em Java: `ProdutoRepository` (JDBC/JPA) usado pelo service; em Go: `repositories.ProdutoRepo` injetado no handler; em Rails: `model` + scopes; em Laravel: `Model::query()`/`Repository`.

## Padrão 7 — Remover Estado Global Mutável / Injetar Dependências (AP-07)
**Antes (JS):**
```js
let globalCache = {};
function logAndCache(k, d){ globalCache[k] = d; }
```
**Depois:** encapsular em instância/injeção:
```js
class CacheService { constructor(){ this._store = {}; } set(k,v){ this._store[k]=v; } get(k){ return this._store[k]; } }
```
Passar `cacheService` por parâmetro (DI) ao invés de importar global.
**Antes (Python):** `db_connection = None` global.
**Depois:** gerenciar conexão dentro de uma classe `Database`/`DatabaseSession` e injetar; `app.app_context()` no composition root.
**Depois (genérico):** injetar a conexão/serviço por construtor/parâmetro em vez de variáveis globais — Java `@Autowired`/Injeção por construtor; Go struct recebendo `*sql.DB`; Rails `config/initializers` + DI; Laravel service container.

## Padrão 8 — Eliminar N+1 com JOIN / Lote (AP-08, AP-13)
**Antes (JS):**
```js
courses.forEach(c => { db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], ...) });
```
**Depois:** uma query com JOIN:
```js
db.all(`
  SELECT c.title, p.amount, p.status, u.name, u.email
  FROM courses c
  LEFT JOIN enrollments en ON en.course_id = c.id
  LEFT JOIN payments p ON p.enrollment_id = en.id
  LEFT JOIN users u ON u.id = en.user_id`, []);
```
**Depois (Python/SQLAlchemy):** `joinedload` / `db.session.query(...).join(...)` em um único acesso.
**Depois (genérico):** o mesmo vale em qualquer ORM — Rails `includes(:enrollments)`, Laravel `with('matriculas')`, JPA `@EntityGraph`/`join fetch`; em SQL puro, um único `SELECT ... LEFT JOIN`.

## Padrão 9 — Remover Endpoints de SQL Cru (AP-09)
**Antes:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query)  # qualquer SQL do cliente
```
**Depois:** remover a rota (ou restringir a whitelist de consultas parametrizadas internas). Nunca executar SQL enviado pelo cliente.

## Padrão 10 — Error Handling Centralizado (AP-11)
**Antes (Python — try/except repetido em cada função):**
```python
except Exception as e:
    return jsonify({"erro": str(e)}), 500
```
**Depois (Flask) — re-raise obrigatório para erros HTTP:**
```python
from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, HTTPException):
        return e  # preserva 404/405/400 do framework, NUNCA vira 500
    app.logger.exception(e)
    return jsonify({"erro": "Erro interno"}), 500
```
> ⚠️ `@app.errorhandler(Exception)` SEM o `isinstance(e, HTTPException)` transforma rota inexistente (404) e método errado (405) em 500 — regressão comum de refactor. Sempre re-encaminhe `HTTPException` com o status original.
**Depois (Express) — dar prioridade a status do erro:**
```js
// middlewares/errorHandler.js
app.use((err, req, res, next) => {
  console.error(err);
  const status = err.status || err.statusCode || 500;
  res.status(status).json({ error: err.message || "Internal Server Error" });
});
```
**Depois (genérico):** o mesmo princípio em qualquer stack — preservar o status do framework (404/405/400) e responder genérico só para erros internos: Java `@ControllerAdvice` + `ResponseStatusException`/`ResponseEntity`; Go middleware que lê `http.StatusNotFound`/erro com `status`; Rails `rescue_from` + `head :not_found`; Laravel `Handler::render` verificando `HttpException`.
> Logar o detalhe no servidor, responder mensagem genérica ao cliente (exceto erros HTTP legítimos, cujo status deve ser mantido).

## Padrão 11 — Middleware de Auth nas Rotas Sensíveis (AP-14)
**Antes:** rota `/api/admin/financial-report` sem auth.
**Depois:**
```js
app.get('/api/admin/financial-report', requireAuth, reportController);
```
**Depois (Python):** decorator/antes_de_requisicao em blueprint admin; verificação de permissão antes de operações de escrita (delete, reset, status).
**Depois (genérico):** rota sensível exige autenticação/autorização em qualquer stack — Go middleware encadeado; Java `@PreAuthorize("hasRole('ADMIN')")`/SecurityFilterChain; Rails `before_action :require_admin`; Laravel middleware `auth:api`/Policy.

## Padrão 12 — Validação de Entrada Reutilizável (AP-15)
**Antes (Python):** checagens manuais repetidas em cada rota.
**Depois:** centralizar num validador/schema (ex: `services/validators.py`, Pydantic, ou helper) chamado antes da ação.
**Depois (Node):** usar Joi/validator ou schema no controller; reutilizar para `create` e `update`.
**Depois (genérico):** validação em camada única, reutilizada por todos os handlers — Java `@Valid` + Bean Validation/DTOs; Go pacote `validators` reutilizado; Rails `ActiveModel::Validations`/`form objects`; Laravel `FormRequest`; Python `Pydantic`/`marshmallow`.

## Padrão 13 — Constantizar Magic Numbers (AP-16)
**Antes:**
```python
if faturamento > 10000: desconto = faturamento * 0.1
```
**Depois:**
```python
DESCONTO_FAIXA_ALTA = 0.10
LIMITE_FAIXA_ALTA = 10000.0
if faturamento > LIMITE_FAIXA_ALTA: desconto = faturamento * DESCONTO_FAIXA_ALTA
```
Colocar em `config` ou módulo de constantes nomeadas.

## Padrão 14 — Renomear Variáveis Criptográficas (AP-17)
**Antes:**
```js
let u = req.body.usr, e = req.body.eml, p = req.body.pwd, cid = req.body.c_id, cc = req.body.card;
```
**Depois:**
```js
const { name, email, password, courseId, cardNumber } = req.body;
```

## Padrão 15 — Migrar APIs Deprecated (AP-18)
- **Flask:** substituir `before_first_request` por `app.before_request`/`with app.app_context()`. Remover `SQLALCHEMY_TRACK_MODIFICATIONS` obsoleto.
- **Express/SQLite3:** substituir callback-hell por Promises (`sqlite3` → `better-sqlite3`/`node:sqlite` com `async/await`).
- **SQLAlchemy:** usar `Model.query` quando disponível; em versões novas priorizar `db.session.execute(select(...))`.
- **Spring Security (Java):** `WebSecurityConfigurerAdapter` → beans de `SecurityFilterChain`; `javax.*` → `jakarta.*` (Boot 3).
- **Go:** `io/ioutil` → `io`/`os`; libs antigas de SQL driver → `database/sql`.
- **Rails:** `before_filter` → `before_action`; `update_attributes` → `update`.
- **Laravel/PHP:** `mysql_*` → PDO; `md5/sha1` p/ senha → `password_hash`.
> Em qualquer stack: ao detectar API obsoleta, use a documentação oficial da versão instalada e migre para o equivalente moderno.

## Padrão 16 — Preservar Contrato de API e Validações (anti-regressão)
Ao reestruturar, não basta "criar views/routes": é preciso reconquistar o contrato da Fase 1.

1. **Inventário (genérico, qualquer stack):** liste TODAS as rotas que o original expõe — o CRUD completo de cada recurso (`GET/POST`, `GET/PUT/DELETE /<recurso>/<id>`), busca/filtros, listagens, autenticação (`/login`), relatórios, `health`, `admin`, rota-raiz (`/`) e quaisquer helper/auxiliares. Não julgue importância — tudo entra no contrato.
2. **Re-registrar:** copie exatamente método + caminho para o novo roteamento (blueprint/router). Uma rota esquecida = contrato quebrado.
3. **Preservar validações:** o controller novo deve repetir as checagens do original (campos obrigatórios, limites de faixa, valores negativos, enumerações/categorias) e retornar os MESMOS status (`400`) — nunca transformar erro de input em `500` por `KeyError`/`TypeError` ao acessar um campo sem validar sua presença.
4. **Teste de paridade (genérico):** rode request real em cada rota (sucesso + casos de erro) e confira o status. Padrões a conferir em qualquer projeto:
   - rota de recurso existente → `2xx`;
   - rota inexistente → `404` (nunca `500`);
   - método errado na rota existente → `405` (nunca `500`);
   - payload sem campo obrigatório / fora da faixa → `400` (nunca `500`);
   - autenticação com credenciais válidas e inválidas → `2xx` e `401` conforme o original.
> Para testar sem subir servidor: Python/Flask `test_client()`, Node `supertest`/`fetch`, Java/Spring `MockMvc`, Go `httptest`, Rails `integration tests`, Laravel `actingAs`/`$this->get(...)`. Aplicável a cenários de validação e 404/405.

## Padrão 17 — DTO/Whitelist (nunca serializar segredos) + serializer único (agnóstico de stack)
**Princípio (vale para TODA linguagem/framework):** nunca devolver a entidade/objeto inteiro; toda resposta de API passa por um **mapeador/DTO com whitelist** de campos públicos. Campos de credencial/hash (`senha`/`password`), `token`, `cvv`, `numero_cartao`, etc., nunca aparecem em retornos, listagens, detalhes, logs ou relatórios — em nada muda a stack.

**Antes (vaza o hash) vs Depois (whitelist) — em várias stacks:**
- **Python:** `def _usuario_to_dict(u): return {..., "senha": u.senha}` → `def _usuario_publico(u): return {"id","nome","email","tipo"}` (sem `senha`/hash).
- **Node/Express:** `res.json(user)` → `const { senha, token, cvv, cardNumber, ...safe } = user; res.json(safe);` (destructuring omite sensíveis).
- **Java/Spring:** devolver `<DadoModelo>` → mapear para `DTO` com só os campos públicos (ex.: `UsuarioDTO { id, nome, email }`).
- **Go:** `json:"-"` nas structs para cada campo sensível (ou um `ToDTO()` que só preenche o público).
- **Rails:** `as_json(only: [:id, :nome, :email])` / slice em vez de serializar o model inteiro.
- **Laravel/PHP:** `$user->makeHidden(['senha_hash'])->toArray()` ou um `Resource`/DTO que só expõe campos permitidos.

**Serializer único + DRY (AP-12):** o mapeador é **um só** e reutilizado por todos os métodos que expõem a entidade (listar, buscar por id, busca, detalhe). Se a mesma monta/enum aparece copiada em 3 funções, é duplicação a corrigir:
- **Python:** `def _produto_to_dict(row): return {...}` usado por `get_todos_produtos`, `get_produto_por_id`, `buscar_produtos`.
- **Java:** um `ProdutoMapper.toDTO(model)` chamado nos controllers/repositórios.
- **Node** **/** **Go** **/** **Rails** **/** **Laravel:** equivalente — uma única função/classe de mapeamento por entidade.

**Regra de ouro:** cada entidade tem **um único ponto de serialização** (whitelist) para saída da API. Concentre-a num arquivo/módulo de mapeamento; nunca `res.json(entity)`/`return model` cru.

## Padrão 18 — Rotas destrutivas/config protegidas ou desativadas (AP-14/AP-09)
Rotas que apagam/escrevem globalmente (`/admin/reset-db`, `/admin/query`, `/delete-X`, `/admin/financial-report`) precisam de guard de segurança. No refactor:
- Se a app legada **não** tinha guard de autenticação, NÃO introduza auth surpresa que quebre o contrato — mas **desative/proteja** rotas destrutivas sensíveis (recomendado: retorno `403` "desabilitado por segurança", como em AP-09) OU mantenha o comportamento original somente se havia guard real.
- **Sinal de problema (projeto 1):** `/admin/reset-db` e `/admin/query` **sem autenticação** no original e ainda expostas no refactor. Adequado: bloquear `/admin/query` (403); para o reset, aplicar o mesmo princípio ou exigir token. Documente a decisão no relatório.
- **Agnóstico de stack:** em Python/Flask (decorator/`before_request`), Express (`app.use`/`requireAuth`), Java (`@PreAuthorize`/filter), Go (middleware), Rails (`before_action`), Laravel (middleware `auth`), o princípio é o mesmo — ação irreversível sem guard ainda pública = finding (AP-14/AP-09).

## Padrão 18 — Manter rotas destrutivas protegidas ou desativadas (AP-14/AP-09)
Rotas como `/admin/reset-db`, `/admin/query`, `/delete-X` removem/escrevem globalmente. No refactor:
- Se a app legada **não** tinha guard de autenticação, NÃO introduza auth surpresa que quebre o contrato — mas **desative/proteja** rotas destrutivas sensíveis (recomendado: retorno `403` "desabilitado por segurança", como em AP-09) OU mantenha o comportamento original apenas se havia guard real.
- **Sinal de problema (do projeto 1):** `/admin/reset-db` (apaga o banco) e `/admin/query` **sem qualquer autenticação** no original e ainda expostas no refactor. Adequado: bloquear `/admin/query` (403) — e, para o reset, aplicar o mesmo princípio ou exigir token. Documente a decisão no relatório.
- Em qualquer stack: rota que executa ação irreversível sem guard, ainda pública = finding (AP-14/AP-09).

---

## Checklist de transformação (aplicar ao final)
- [ ] Todo anti-pattern da auditoria tem padrão aplicado
- [ ] Sem queries concatenadas, sem segredos hardcoded, sem senha em texto puro
- [ ] **Nenhuma resposta serializa `senha`/`hash`/`token`/`cvv` (DTO whitelist)**
- [ ] Controllers sem regra pesada; banco só em models
- [ ] Error handler centralizado; responses genéricas; **404/405/400 do framework preservados (re-raise HTTPException)**
- [ ] **TODOS os endpoints do contrato da Fase 1 re-registrados (mesma rota + método)**
- [ ] **Validações, mensagens e códigos de status originais preservados**
- [ ] **Seed com senha JÁ hashada; login testado contra o banco legado existente**
- [ ] Middlewares globais originais (ex: `CORS`) mantidos
- [ ] App inicia sem erros e cada endpoint responde com o comportamento original (validação executada)