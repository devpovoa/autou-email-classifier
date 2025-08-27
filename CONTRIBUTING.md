# Contributing to AutoU Email Classifier

Obrigado pelo seu interesse em contribuir com o projeto AutoU Email Classifier! Este documento fornece diretrizes para contribuições.

## 🚀 Getting Started

### Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Git

### Setup do Ambiente de Desenvolvimento

1. **Clone e configure o projeto**:
```bash
git clone <repository_url>
cd Processo_Seletivo
./scripts/dev-setup.sh
```

2. **Configure variáveis de ambiente**:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

3. **Inicie o ambiente de desenvolvimento**:
```bash
docker-compose up app-dev
```

## 📋 Padrões de Desenvolvimento

### Git Workflow

1. **Branches**:
   - `main`: Branch principal (produção)
   - `develop`: Branch de desenvolvimento
   - `feature/`: Novas funcionalidades
   - `bugfix/`: Correções de bugs
   - `hotfix/`: Correções urgentes

2. **Commits Convencionais**:
   Usamos [Conventional Commits](https://conventionalcommits.org/) para padronizar mensagens:

   ```
   <type>(<scope>): <description>
   
   <body>
   
   <footer>
   ```

   **Tipos permitidos**:
   - `feat`: Nova funcionalidade
   - `fix`: Correção de bug
   - `docs`: Documentação
   - `style`: Formatação (sem mudança funcional)
   - `refactor`: Refatoração de código
   - `test`: Testes
   - `chore`: Tarefas de manutenção
   - `ci`: Configurações de CI/CD
   - `perf`: Melhorias de performance

   **Exemplos**:
   ```bash
   git commit -m "feat(api): add email batch classification endpoint"
   git commit -m "fix(docker): resolve container startup timeout issue"
   git commit -m "docs: update API documentation with new endpoints"
   ```

### Padrões de Código

1. **Formatação**:
   - **Black**: Formatação automática
   - **isort**: Organização de imports
   - **flake8**: Linting

   ```bash
   # Aplicar formatação
   docker-compose --profile lint run --rm lint
   ```

2. **Estrutura de Código**:
   - Siga PEP 8
   - Use type hints
   - Docstrings em funções públicas
   - Máximo 88 caracteres por linha

3. **Testes**:
   - Cobertura mínima: 85%
   - Testes unitários para lógica de negócio
   - Testes de integração para APIs
   - Mocks para dependências externas

   ```bash
   # Executar testes
   ./scripts/build-and-test.sh
   
   # Testes específicos
   pytest tests/test_units.py -v
   ```

## 🔄 Processo de Contribuição

### 1. Preparação

```bash
# 1. Fork do repositório no GitHub
# 2. Clone seu fork
git clone https://github.com/seu-usuario/Processo_Seletivo.git
cd Processo_Seletivo

# 3. Adicione o upstream
git remote add upstream https://github.com/original/Processo_Seletivo.git

# 4. Configure ambiente
./scripts/dev-setup.sh
```

### 2. Desenvolvimento

```bash
# 1. Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolva sua funcionalidade
# ... código ...

# 3. Teste localmente
./scripts/build-and-test.sh --lint

# 4. Commit suas mudanças
git add .
git commit -m "feat(scope): description of changes"
```

### 3. Pull Request

1. **Atualize sua branch**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push para seu fork**:
```bash
git push origin feature/nova-funcionalidade
```

3. **Crie Pull Request**:
   - Título descritivo
   - Descrição detalhada das mudanças
   - Screenshots se aplicável
   - Link para issues relacionadas

### 4. Checklist do PR

- [ ] Código segue padrões do projeto
- [ ] Testes passando (110/110)
- [ ] Cobertura >= 85%
- [ ] Documentação atualizada
- [ ] Commit messages seguem padrão
- [ ] Docker build funcionando
- [ ] Sem secrets hardcoded

## 🧪 Testing Guidelines

### Estrutura de Testes

```
tests/
├── test_units.py         # Testes unitários
├── test_integration.py   # Testes de integração
├── test_routes.py        # Testes de API
├── test_performance.py   # Testes de performance
└── test_utils.py         # Testes de utilitários
```

### Escrevendo Testes

1. **Nomenclatura**:
   ```python
   def test_should_classify_urgent_email_when_contains_keywords():
       # Arrange
       # Act
       # Assert
   ```

2. **Mocks**:
   ```python
   @patch('app.services.ai.openai_client')
   def test_ai_classification_with_mock(mock_client):
       # Test with mocked external dependency
   ```

3. **Fixtures**:
   ```python
   @pytest.fixture
   def sample_email():
       return "Preciso de ajuda urgente com o sistema!"
   ```

### Executando Testes

```bash
# Todos os testes
docker-compose --profile test run --rm test

# Testes específicos
pytest tests/test_units.py::test_specific_function -v

# Com coverage
pytest --cov=app --cov-report=html

# Performance tests
pytest tests/test_performance.py -v
```

## 📦 Docker Development

### Build e Test

```bash
# Development build
docker build --target development -t autou-classifier:dev .

# Production build
docker build --target production -t autou-classifier:prod .

# Test com Docker
./scripts/build-and-test.sh
```

### Docker Compose

```bash
# Desenvolvimento
docker-compose up app-dev

# Testes
docker-compose --profile test run --rm test

# Linting
docker-compose --profile lint run --rm lint
```

## 📚 Documentação

### Atualizando Docs

1. **README.md**: Funcionalidades principais
2. **API Docs**: Swagger UI automático em `/docs`
3. **DOCKER_SETUP.md**: Instruções Docker
4. **Docstrings**: Documentação inline

### Formato de Docstrings

```python
def classify_email(text: str, provider: str = "OpenAI") -> dict:
    """
    Classifica um email usando IA ou heurísticas.
    
    Args:
        text: Conteúdo do email para classificar
        provider: Provedor de IA ("OpenAI" ou "HF")
    
    Returns:
        dict: Resultado da classificação com categoria e confiança
    
    Raises:
        ValueError: Quando o texto está vazio
        AIProviderError: Quando há erro na API de IA
    """
```

## 🐛 Reportando Issues

### Bug Reports

Use o template:

```markdown
## Bug Description
Descrição clara do problema

## Steps to Reproduce
1. Vá para...
2. Clique em...
3. Veja erro...

## Expected Behavior
O que deveria acontecer

## Actual Behavior
O que aconteceu

## Environment
- OS: 
- Python: 
- Docker: 
- Browser: 

## Additional Context
Screenshots, logs, etc.
```

### Feature Requests

```markdown
## Feature Summary
Breve descrição da funcionalidade

## Problem Statement
Que problema isso resolve?

## Proposed Solution
Como deveria funcionar?

## Alternatives Considered
Outras opções consideradas

## Additional Context
Mockups, referências, etc.
```

## ⚡ Performance Guidelines

### Benchmarks Esperados

- Classificação simples: < 5s
- Upload PDF: < 30s
- Startup time: < 30s
- Memory usage: < 512MB

### Otimizações

1. **Cache**: Use cache para resultados repetidos
2. **Async**: Operações I/O assíncronas
3. **Batch**: Processamento em lote quando possível
4. **Lazy Loading**: Carregue modelos sob demanda

## 🔒 Security Guidelines

### Práticas de Segurança

1. **Secrets**: Nunca commite secrets
2. **Input Validation**: Sempre valide inputs
3. **Dependencies**: Mantenha dependências atualizadas
4. **Docker**: Use usuário não-root

### Verificações

```bash
# Scan de vulnerabilidades
docker scout cves autou-classifier:latest

# Verificar secrets
git-secrets --scan

# Dependency check
safety check -r requirements.txt
```

## 🚀 Release Process

### Versionamento

Usamos [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `1.0.0`: Versão inicial
- `1.1.0`: Nova funcionalidade
- `1.1.1`: Bug fix

### Criando Release

```bash
# 1. Atualizar versão
git tag v1.1.0

# 2. Push tags
git push origin v1.1.0

# 3. GitHub Actions fará deploy automático
```

## 📞 Suporte

- **GitHub Issues**: Para bugs e features
- **Discussions**: Para perguntas gerais
- **Email**: Para questões sensíveis

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

Obrigado por contribuir! 🎉
