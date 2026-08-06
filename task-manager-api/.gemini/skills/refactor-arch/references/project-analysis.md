# Análise de Projeto — Heurísticas de Detecção

Use esta referência na **Fase 1** para detectar a stack, o banco de dados e mapear a arquitetura de forma agnóstica de tecnologia.

## 1. Detecção de Linguagem

| Sinal no código | Linguagem |
|---|---|
| `from flask import`, `import`, `def `, `if __name__ == "__main__"` | Python |
| `const x = require(...)`, `import ... from`, `module.exports`, `app.listen(...)` | JavaScript/Node.js |
| `interface Foo`, `type Bar =`, `export const`, `async (req: ...)` em `.ts` | TypeScript |
| Classes com modificadores `public/private`, `package `, `namespace `, `@SpringBootApplication` | Java |
| `<?php`, `function foo()` em arquivos `.php`, `->get()`/`->post()` | PHP |
| `gemfile`/`gem `, `def ` em arquivos `.rb`, `Rails.application` | Ruby |
| `package main`, `func main()`, `import "net/http"` | Go |
| `using Microsoft.AspNetCore`, `[ApiController]`, `public void Main` | C# / .NET |

Confirme também pelos arquivos de manifest:
- `requirements.txt`, `Pipfile`, `pyproject.toml` → Python
- `package.json`, `yarn.lock`, `package-lock.json` → Node.js/TypeScript
- `tsconfig.json` → TypeScript
- `Gemfile` → Ruby, `pom.xml`/`build.gradle` → Java, `composer.json` → PHP
- `go.mod` → Go, `csproj`/`*.sln` → C#/.NET

## 2. Detecção de Framework

| Sinal | Framework | Linguagem |
|---|---|---|
| `flask.Flask`, blueprints `Blueprint(...)`, `add_url_rule` | Flask | Python |
| `from flask_sqlalchemy import SQLAlchemy`, `db.Model` | Flask + SQLAlchemy | Python |
| `from fastapi import FastAPI`, decorators `@app.get` | FastAPI | Python |
| `from django` | Django | Python |
| `require('express')`, `app.get/post/use`, middleware | Express | Node.js |
| `nest`/`NestFactory`, `@Controller`, `@Module` | NestJS | Node.js |
| `from bottle`, `@route` | Bottle | Python |
| `@SpringBootApplication`, `@RestController`, `@RequestMapping` | Spring Boot | Java |
| `HttpServer`, `ServeMux`, `r.HandleFunc` | net/http | Go |
| `gin.Default()`, `router := gin.New()` | Gin | Go |
| `Rails.application.routes.draw`, `ActiveRecord` | Rails | Ruby |
| `namespace :api` , `get :index`, `resources` | Grape/Sinatra | Ruby |
| `$router = new Router()`, `->get('/'...)`, Blade `@extends` | Laravel | PHP |
| `get_route`, `$app->get` | Slim | PHP |
| `CreateBuilder`, `.AddControllers()`, `[Route("[controller]")]` | ASP.NET Core | C# |

**Versão do framework:** leia o manifesto.
- Python: `requirements.txt` (`flask==3.1.1`) ou `pip freeze`.
- Node/TS: `package.json` → `dependencies`.
- Java: `pom.xml` → `dependencies`; Maven/Gradle.
- Go: `go.mod`; Ruby: `Gemfile.lock`/`gemspec`; PHP: `composer.json`; C#: `.csproj`/`packages.config`.

## 3. Detecção de Banco de Dados

| Sinal | Banco |
|---|---|
| `sqlite3.connect`, `:memory:`, `loja.db`, `.db`, `SQLALCHEMY_DATABASE_URI = 'sqlite:///...'` | SQLite |
| `psycopg2`, `postgresql://`, `pg.Connect` (Go), `PG::Connection` (Ruby) | PostgreSQL |
| `pymysql`, `mysql.connector`, `mysql://`, `go-sql-driver/mysql` | MySQL |
| `MongoClient`, `mongodb://`, `go.mongodb.org/mongo-driver` | MongoDB |
| `database/sql` (Go), `java.sql.Connection`, `ActiveRecord::Base` | SQL genérico (via driver/ORM) |

Liste as tabelas criadas (instruções `CREATE TABLE`/`CREATE TABLE IF NOT EXISTS` ou classes `db.Model`).

## 4. Domínio da Aplicação

Inferir a partir de:
- Recursos/rotas: `/produtos`, `/pedidos`, `/usuarios` → E-commerce.
- Tabelas: `users`, `courses`, `enrollments`, `payments` → LMS / Educação.
- Nomes de entidades e endpoints.

Exemplo: "E-commerce API (produtos, pedidos, usuários)" ou "LMS API com fluxo de checkout".

## 5. Mapeamento da Arquitetura Atual

Classifique o nível de organização:

| Observação | Classificação |
|---|---|
| Tudo em 1–4 arquivos; lógica de banco, negócio e rotas no mesmo arquivo | Monolítica / God Class |
| Há pastas `models/`, `routes/`, `services/`, `utils/`, mas misturam responsabilidades | Parcialmente em camadas |
| Models + Controllers + Views/Routes claramente separados | Quase-MVC |
| Múltiplos projetos/códigos num só arquivo (God object) | Monolítica aglomerada |

**Como mapear:**
- Liste os arquivos-fonte e o papel de cada um (entry point, camada de dados, roteamento, lógica de negócio).
- Identifique onde a lógica de negócio vive (controllers? models?) — isso revela violações de separação de responsabilidades.
- Contagem de arquivos e linhas: use `rg`/grep de forma a obter contagens reais (ex. `rg -c "" *.py` e `(Get-Content app.py).Count` no Windows).

> **Fluxo:** enumero os arquivos → classifico stack → leio os principais → conto arquivos/LoC → derivo domínio e arquitetura.