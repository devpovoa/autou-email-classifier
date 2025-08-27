# Configuração de Qualidade de Código

## 🎯 Filosofia

Este projeto utiliza uma abordagem **harmonizada** para qualidade de código, onde cada ferramenta tem sua responsabilidade específica:

- **Black**: Formatação automática e consistente do código
- **isort**: Organização automática dos imports  
- **Flake8**: Análise de qualidade, erros lógicos e padrões Python

## 🔧 Configuração

### Black (Formatador)
- **Versão**: 24.8.0
- **Linha máxima**: 88 caracteres (padrão)
- **Responsabilidade**: Formatação automática de código

### isort (Organização de Imports)
- **Versão**: 5.13.2
- **Perfil**: `black` (compatibilidade total)
- **Responsabilidade**: Ordenação e organização de imports

### Flake8 (Análise de Qualidade)
- **Versão**: 7.1.1
- **Configuração**: `.flake8` na raiz do projeto
- **Responsabilidade**: Detecção de erros lógicos, código não utilizado, etc.

## 📁 Arquivo .flake8

```ini
[flake8]
max-line-length = 88
extend-ignore = E203,W503,E501
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    htmlcov,
    coverage,
    logs,
    uploads,
    .pytest_cache
per-file-ignores =
    __init__.py:F401
```

### Códigos Ignorados

- **E203**: Espaço antes de ':' - conflito com Black
- **W503**: Quebra de linha antes de operador binário - conflito com Black  
- **E501**: Linha muito longa - **Black é responsável pelo comprimento**

### Exclusões

Diretórios automaticamente excluídos da análise:
- Controle de versão (`.git`)
- Cache Python (`__pycache__`, `.pytest_cache`)
- Ambientes virtuais (`.venv`, `venv`)
- Relatórios de cobertura (`htmlcov`, `coverage`)
- Diretórios de runtime (`logs`, `uploads`)

## 🚀 Comandos de Uso

### Verificação (CI/CD)
```bash
# Verificar formatação
black --check --diff app/ tests/ main.py

# Verificar imports
isort --profile black --check-only --diff app/ tests/ main.py

# Verificar qualidade
flake8 app/ tests/ main.py
```

### Aplicação Local
```bash
# Aplicar formatação
black app/ tests/ main.py

# Organizar imports  
isort --profile black app/ tests/ main.py

# Verificar qualidade
flake8 app/ tests/ main.py
```

### Docker Compose
```bash
# Executar todas as verificações
docker compose --profile lint run --rm lint
```

## 🎪 Integração CI/CD

O pipeline GitHub Actions executa as verificações na seguinte ordem:

1. **Black**: Verifica se o código está formatado
2. **isort**: Verifica se os imports estão organizados
3. **Flake8**: Verifica qualidade do código

Se qualquer verificação falhar, o pipeline para e indica os problemas.

## 💡 Resolução de Conflitos

### Black vs Flake8 (E501)
- **Problema**: Black às vezes mantém linhas > 88 chars quando não consegue quebrar elegantemente
- **Solução**: Flake8 ignora E501, deixando Black responsável pelo comprimento
- **Resultado**: Formatação consistente sem conflitos

### Black vs isort
- **Problema**: Diferentes formas de organizar imports
- **Solução**: isort usa perfil `black` para compatibilidade total
- **Resultado**: Imports organizados no padrão Black

## 🔄 Pre-commit Hooks

O projeto utiliza hooks que executam automaticamente antes de cada commit:

```yaml
# .pre-commit-config.yaml (conceitual)
repos:
  - repo: local
    hooks:
      - id: lint
        name: Code Quality Checks
        entry: docker compose --profile lint run --rm lint
        language: system
        pass_filenames: false
```

## 📈 Benefícios

1. **Consistência**: Código sempre formatado da mesma forma
2. **Produtividade**: Formatação automática, menos discussões de estilo
3. **Qualidade**: Detecção automática de problemas
4. **CI/CD**: Verificação automática em cada push
5. **Harmonia**: Ferramentas trabalham juntas sem conflitos

## 🛠️ Troubleshooting

### "Black não formatou uma linha longa"
✅ **Normal**: Black mantém linhas longas quando não consegue quebrar elegantemente  
✅ **Solução**: Flake8 ignora E501, deixando Black decidir

### "Pre-commit hooks falhando"  
1. Execute `black app/ tests/ main.py`
2. Execute `isort --profile black app/ tests/ main.py`
3. Verifique com `flake8 app/ tests/ main.py`
4. Commit novamente

### "Conflitos entre ferramentas"
✅ **Configuração atual resolve automaticamente todos os conflitos conhecidos**

## 📝 Evolução

Esta configuração foi desenvolvida através de iterações para resolver:
1. ✅ Conflitos docker-compose → docker compose 
2. ✅ Conflitos Black vs Flake8 (E501)
3. ✅ Padronização de comandos em CI/CD
4. ✅ Centralização de configuração

**Status**: ✅ Configuração estável e harmonizada
