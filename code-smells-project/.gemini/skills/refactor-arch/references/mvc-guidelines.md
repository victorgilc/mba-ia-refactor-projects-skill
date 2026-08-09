# Guidelines de Arquitetura — Padrão MVC Alvo

Use na **Fase 3** para definir a estrutura de destino. As responsabilidades de cada camada devem ser respeitadas, independente da tecnologia.

## Visão Geral das Camadas

| Camada | Responsabilidade | Não deve fazer |
|---|---|---|
| **Model** | Abstração e acesso a dados (entidades, repositórios, queries parametrizadas) | Não contém lógica HTTP, não expõe rotas |
| **View / Routes** | Roteamento da API (mapear URLs → controllers); formatar a resposta HTTP | Não acessa banco diretamente, não tem regra de negócio |
| **Controller** | Orquestrar o fluxo: receber request (via rotas), chamar services/models, montar contexto/interação | Não contém SQL, não implementa regra de negócio pesada |
| **Service / Use-Case** | Regras de negócio (cálculos, descontos, validações de domínio, notificações) | Não expõe HTTP, não acessa banco direto (usa models) |
| **Config** | Configuração central (secrets via env, constantes, conexões) | Não contém segredos hardcoded |
| **Middleware / Error Handler** | Tratamento centralizado de erros, autenticação/autorização | Não contém lógica de negócio |

## Estrutura de Diretórios Alvo (genérica)

```
src/                                    # (ou o dir de entrada do projeto)
├── config/                             # (ou config.js/application.properties/settings.rb)
│   └── settings.py                     # usa env vars, sem hardcoded
├── models/
│   ├── produto_model.py                # entidades + repositórios
│   └── usuario_model.py
├── views/                              # ou routes/
│   └── routes.py                       # mapeia URL → controller
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/
│   └── error_handler.py                # tratamento central de erros
└── app.py                              # composition root (entry point)
```

> Adapte os nomes/quantidade de arquivos à stack, mas preserve estas camadas lógicas. Exemplos por stack: Node → `src/routes/`, `src/controllers/`, `src/models/`; Java → `controllers/`/`services/`/`repositories/`; Go → `handlers/`, `services/`, `repositories/`; Ruby/Rails → `controllers/`, `models/`, `services/`; PHP/Laravel → `Http/Controllers/`, `Models/`, `Services/`.

## Regras Obrigatórias na Refatoração

1. **Config sem hardcoded:**
   - Python: `SECRET_KEY = os.environ.get("SECRET_KEY", ...)` — nunca no código literal.
   - Node/TS: `const { SECRET_KEY } = process.env;` em `config.js`/`config.ts`.
   - Java: `@Value("${SECRET_KEY}")`/env vars; Spring profile `application-*.properties`.
   - Go: `os.Getenv("SECRET_KEY")` em `config/config.go`.
   - Ruby: `ENV.fetch("SECRET_KEY")` em config inicializador.
   - PHP: `getenv(...)`/`$_ENV` no arquivo `config/`.
2. **Segurança de banco:** toda query SQL parametrizada (nunca concatenação).
3. **Senhas:** hash com lib padrão (`bcrypt`/`pbkdf2`); nunca texto puro, nunca cripto caseira.
4. **Composition Root:** `app.py`/`app.js` apenas monta a stack e registra o roteamento; nenhuma regra de negócio nele.
5. **Error handling centralizado:** um handler único para a app; responder mensagens genéricas e logar o detalhe; nunca retornar stack trace/segredos ao cliente. **IMPORTANTE — não engolir erros do framework:** o handler deve `raise`/re-encaminhar `HTTPException` (404, 405, 400), respondendo 5xx genérico SOMENTE para erros internos. Registrar `@app.errorhandler(Exception)` sem re-raise transforma rotas inexistentes (404) e métodos errados (405) em 500.
6. **Dependency Injection:** serviços/tipos injetados (evitar estado global mutável e imports circulares acoplados).
7. **Manter contrato de API (paridade total):** TODAS as rotas, métodos e códigos de status originais continuam existindo e respondendo igual, independente da stack. Reforce com a lista de endpoints da Fase 1: todo recurso (CRUD completo — GET/POST/PUT/DELETE), busca/filtros, listagens, relatórios, `health`, rotas administrativas e rotas-raiz devem continuar registrados, mesmo que não pareçam "importantes".
8. **Preservar validação de entrada:** campos obrigatórios, faixas (ex: preço/estoque >= 0, limites de tamanho, categorias válidas) e os status retornados (400/401/201/200) devem ser mantidos do original — refatorar não pode descartar validações nem virar erros em 500 por `KeyError`.
9. **Preservar middlewares globais originais** (ex: `CORS(app)` com `flask-cors`) para não quebrar consumidores cross-origin.
10. **Seed com senha hashada + migração:** ao introduzir hash de senha, o seed da app refatorada deve inserir senhas JÁ hashadas, e deve migrar/re-seed usuários que estejam em texto puro. Nunca comparar hash de entrada contra texto puro armazenado (quebra o login de usuários existentes).
11. **Nunca serializar campos sensíveis (DTO whitelist):** toda resposta (listar, buscar, detalhar, login) usa um mapeador/whitelist de **campos públicos**. Senha/hash (`senha`/`password`), `token`, `cvv`, `numero_cartao` não aparecem em retorno nem em logs. Cada entidade tem **um único serializer** reutilizado (DRY / anti-AP-20, anti-AP-12).
12. **Config carrega `.env`/dotenv no TOPO, antes de ler env vars:** nunca dependa de o framework carregar o `.env` depois (ex.: dentro de `app.run()`/boot) — senão o config importado antes lê valores vazios e o `.env` é ignorado em silêncio (AP-23 / Padrão 22).
13. **Ao migrar API deprecated, remover também a config/flag obsoleta correlata** (ex.: `SQLALCHEMY_TRACK_MODIFICATIONS`) — não só a chamada (AP-25 / Padrão 23).
14. **Sem token de autenticação falso:** login não pode devolver um "token" que nenhuma rota valida. Implementar guard real OU desativar/proteger rotas destrutivas (403) e documentar a decisão (AP-24 / Padrões 11 e 18).
15. **Eliminar N+1 em TODOS os pontos de leitura:** listagem, detalhe por id, contagens de registros relacionados (ex.: listar entidades com `count` de filhos), relatórios e stats — nenhum `SELECT`/`Query` dentro de `for` (AP-27 / Padrão 25).
16. **Remover código morto deixado pela refatoração:** imports, helpers, constantes e funções sem chamador (grep + linter de unused) (AP-26 / Padrão 24).

> O entry point é o único responsável por montar todas as rotas; se uma rota do contrato não aparece no mapeamento, a refatoração está incompleta.

## Exemplos por stack

**Python/Flask — composition root**
```python
from app_setup import create_app, db
from config import config
app = create_app(config)
with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

**Node/Express — composition root**
```js
const express = require('express');
const { config } = require('./config');
const app = express();
app.use(express.json());
require('./routes')(app);
app.use(require('./middlewares/errorHandler'));
app.listen(config.port, () => console.log(`Server on ${config.port}`));
```

**Java/Spring Boot — composition root**
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args); // varre controllers/services/repositories
    }
}
```

**Go/net/http — composition root**
```go
func main() {
    db := config.NewDatabase()          // DI
    mux := http.NewServeMux()
    routes.Register(mux, handlers.New(db)) // controllers recebem deps injetadas
    http.ListenAndServe(":"+config.Port(), middleware.WithErrorHandler(mux))
}
```

**Ruby/Rails — composition root**
```ruby
Rails.application.routes.draw do
  resources :produtos, controller: 'produtos'  # routes → controllers
end
```

**PHP/Laravel — composition root**
```php
// routes/api.php
Route::resource('produtos', ProdutoController::class);
// bootstrap/app.php é o composition root (middlewares, service providers)
```

## Princípios de qualidade aplicados à refatoração

Independente da stack, o código refatorado deve respeitar SOLID, DRY e KISS:

| Princípio | O que significa na prática | Sinal de violação |
|---|---|---|
| **S** — Single Responsibility | Cada classe/módulo/método tem uma única razão para mudar (model acessa dados, controller orquestra, service aplica regra, routes mapeiam) | God class; função que faz roteamento + banco + regra |
| **O** — Open/Closed | Estender comportamento sem editar código existente (ex: mapa de validações/regras, não cadeia gigante de `if/elif`) | Novos casos exigem reescrever a função inteira |
| **L** — Liskov | Tipos/subtipos que podem substituir a base sem quebrar o contrato | Herança onde o filho muda o contrato do pai |
| **I** — Interface Segregation | Interfaces pequenas e específicas; cliente não depende do que não usa | Interfaces "god" com métodos inúteis ao chamador |
| **D** — Dependency Inversion | Depender de abstrações/contratos; injetar `Database`/`Service`, não importar estado/instância global | Import global direto, acoplamento circular |
| **DRY** | Não repetir lógica: validação, queries, construção de resposta, conexão | Mesmo bloco copiado em várias funções/controllers |
| **KISS** | Solução mais simples que atende ao contrato original; sem camadas/abstrações desnecessários | Extrair service/abstração para método trivial só para "parecer MVC" |

> **Limite:** não sacrifique o contrato original nem adicione complexidade por dogma. Se a biblioteca padrão resolve (ex: `werkzeug.security` para hash), use — não reimplemente (DRY + segurança). Se o projeto é simples, um controller direto pode ser preferível a uma camada de service extra (KISS).

## Critério de "feito" da estrutura
- entry point claro e enxuto (composition root)
- config isolada, sem segredos
- models abstraem dados
- routes/views separadas
- controllers concentram o fluxo
- error handler centralizado (que NÃO transforma 404/405 em 500)
- app inicia sem erros e TODOS os endpoints do contrato da Fase 1 respondem com o mesmo método e status
- validações, mensagens e códigos de status originais preservados
- senha hashada em seed e compatível com login (migração aplicada)
- `.env`/dotenv carregado no topo do config (nenhuma env var lida antes)
- config/flag deprecated removida após migração de API obsoleta
- rotas destrutivas protegidas/desativadas ou decisão de auth documentada (sem token falso)
- N+1 eliminado em todos os pontos de leitura (detalhe, contagens, relatórios, stats)
- código morto/imports sem chamador removidos