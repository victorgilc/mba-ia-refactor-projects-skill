# Template de Relatório de Auditoria

Use na **Fase 2**. Todo relatório SEGUE este formato padronizado (preserve os marcadores/cabeçalhos).

## Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<N> lines of code

## Summary
CRITICAL: <X> | HIGH: <Y> | MEDIUM: <Z> | LOW: <W>

## Findings

### [CRITICAL] <Nome do Anti-Pattern>
File: <arquivo>:<linha1-linhaN>
Description: <descrição concisa do problema e onde ocorre>
Impact: <por que é grave / o que pode acontecer>
Recommendation: <ação corretiva concreta>

### [HIGH] <Nome do Anti-Pattern>
File: <arquivo>:<linha>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <Nome do Anti-Pattern>
...

### [LOW] <Nome do Anti-Pattern>
...

================================
Total: <N> findings
================================
```

## Regras de Formatação

1. **Ordenação:** listar findings de CRITICAL → HIGH → MEDIUM → LOW. Nunca embaralhar.
2. **Localização exata:** todo finding tem `File:<arquivo>:<linha>` (ou faixa de linhas). Sem arquivo/linha, não é um achado válido.
3. **Summary** deve estar logo após `Project/Stack/Files`.
4. Cada `Recommendation` precisa ser acionável e vinculada a um padrão do playbook quando aplicável.
5. Seu relatório deve refletir os **anti-patterns reais** encontrados; se uma categoria tem zero, escreva `0`.

## Salvar em arquivo (obrigatório)

O relatório da Fase 2 **sempre deve ser gravado em disco** em `../reports/audit-project-N.md` — nunca apenas exibido no terminal. `N` é o número do projeto no repositório:

- `code-smells-project` (projeto 1) → `../reports/audit-project-1.md`
- `ecommerce-api-legacy` (projeto 2) → `../reports/audit-project-2.md`
- `task-manager-api` (projeto 3) → `../reports/audit-project-3.md`

Regras:
1. Se a pasta `reports/` não existir na raiz do repositório, crie-a.
2. Identifique o número do projeto pelo diretório em execução (1, 2 ou 3) e use `audit-project-N.md` no nome do arquivo.
3. Grave o arquivo com o MESMO conteúdo exibido ao usuário (formato do template abaixo).

## Exemplo completo

```
===============================
ARCHITECTURE AUDIT REPORT
===============================
Project: code-smells-project
Stack:   <linguagem> + <framework>-<versão>   (ex: Python + Flask 3.1.1, Node + Express 4.18.2, Java + Spring Boot 3.2, Go + net/http, Ruby + Rails 7, PHP + Laravel 11)
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:28
Description: Query montada por concatenação de string com dado do usuário na função get_produto_por_id.
Impact: Um request controlado pode injetar SQL e ler/modificar todo o banco.
Recommendation: Usar queries parametrizadas com placeholder `?` (cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))).

### [CRITICAL] Credenciais Hardcoded
File: app.py:7
Description: SECRET_KEY definida em claro dentro do código-fonte.
Impact: Exposição de segredo; compromete sessões e dados.
Recommendation: Mover para variável de ambiente e ler via os.environ.

...(demais findings ordenados por severidade)...

================================
Total: 9 findings
================================
```

## Pré-condição — Confirmação
Após gerar, **salvar em `../reports/audit-project-N.md`** e exibir o relatório, **PARE** e pergunte:

```
Total: <N> findings
Relatório salvo em ../reports/audit-project-N.md
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [y/n]
```

Só inicie a Fase 3 com resposta afirmativa (y/yes).