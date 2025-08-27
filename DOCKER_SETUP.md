# AutoU Email Classifier - Docker & CI/CD Setup

Este documento descreve a configuração Docker e CI/CD implementada para o projeto AutoU Email Classifier.

## 🐳 Configuração Docker

### Multi-stage Dockerfile

O projeto utiliza um Dockerfile multi-stage para otimizar o build:

- **Development Stage**: Inclui todas as ferramentas de desenvolvimento e teste
- **Production Stage**: Imagem otimizada apenas com dependências de produção

### Docker Compose

Configuração com múltiplos perfis de serviços:

```bash
# Desenvolvimento
docker-compose up app-dev

# Produção
docker-compose up app

# Testes
docker-compose --profile test run --rm test

# Linting
docker-compose --profile lint run --rm lint
```

## 🚀 Scripts de Automação

### 1. dev-setup.sh
Script para configuração inicial do ambiente de desenvolvimento:

```bash
./scripts/dev-setup.sh
```

**Funcionalidades:**
- Verifica dependências do sistema (Docker, Docker Compose)
- Cria arquivo .env com configurações padrão
- Configura diretórios necessários
- Configura hooks do git (opcional)
- Constrói ambiente de desenvolvimento
- Executa testes de verificação

### 2. build-and-test.sh
Script para build e testes automatizados:

```bash
# Desenvolvimento com testes
./scripts/build-and-test.sh

# Produção
./scripts/build-and-test.sh --target production

# Apenas linting
./scripts/build-and-test.sh --lint --no-tests

# Modo verboso
./scripts/build-and-test.sh -v
```

**Funcionalidades:**
- Build de imagens Docker (development/production)
- Execução de testes automatizados
- Verificação de qualidade de código (linting)
- Teste de inicialização da aplicação
- Output colorido e logging detalhado

### 3. deploy.sh
Script para deploy em produção com rollback automático:

```bash
# Deploy padrão
./scripts/deploy.sh

# Deploy com porta customizada
./scripts/deploy.sh --port 8080

# Deploy sem backup
./scripts/deploy.sh --no-backup

# Deploy forçado (sem health checks)
./scripts/deploy.sh --force
```

**Funcionalidades:**
- Backup automático da versão atual
- Build e deploy da nova versão
- Health checks com timeout configurável
- Rollback automático em caso de falha
- Limpeza de imagens antigas

## ⚙️ GitHub Actions CI/CD

### Pipeline Principal (.github/workflows/ci-cd.yml)

Pipeline completo com múltiplos estágios:

1. **Lint**: Verificação de qualidade de código
2. **Test**: Execução de testes unitários e de integração
3. **Build**: Build de imagens Docker multi-plataforma
4. **Deploy**: Deploy automático (branches principais)
5. **Performance**: Testes de performance
6. **Security**: Scanning de segurança

### Pipeline Docker (.github/workflows/docker-tests.yml)

Testes específicos para Docker:

1. **Docker Build**: Teste de build multi-stage
2. **Docker Compose**: Teste de funcionamento com docker-compose
3. **Health Checks**: Validação de health checks
4. **Multi-platform**: Build para múltiplas arquiteturas

### Triggers de CI/CD

- **Push**: Branches `main`, `develop`, `staging`
- **Pull Request**: Para qualquer branch
- **Schedule**: Execução noturna (opcional)
- **Manual**: Dispatch manual via GitHub UI

## 📊 Monitoramento e Observabilidade

### Health Checks

- **Endpoint**: `/health`
- **Docker Health Check**: Configurado automaticamente
- **Timeout**: 10s com 3 tentativas
- **Interval**: 30s

### Logging

- **Structured Logging**: JSON format em produção
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Configurado via Docker logging driver

### Métricas

- **Coverage**: Relatórios de cobertura de testes
- **Performance**: Métricas de tempo de resposta
- **Security**: Scanning de vulnerabilidades

## 🔧 Configuração de Ambiente

### Variáveis de Ambiente (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Secrets do GitHub

Configure os seguintes secrets no repositório:

- `OPENAI_API_KEY`: Chave da API OpenAI
- `DOCKER_USERNAME`: Username do Docker Hub
- `DOCKER_PASSWORD`: Password/Token do Docker Hub

## 🛠️ Comandos Úteis

### Desenvolvimento Local

```bash
# Setup inicial
./scripts/dev-setup.sh

# Desenvolvimento
docker-compose up app-dev

# Testes
./scripts/build-and-test.sh

# Linting
docker-compose --profile lint run --rm lint
```

### Produção

```bash
# Build produção
./scripts/build-and-test.sh --target production

# Deploy
./scripts/deploy.sh

# Logs
docker logs -f autou-classifier-prod

# Status
docker ps --filter name=autou-classifier-prod
```

### Troubleshooting

```bash
# Verificar saúde do container
curl http://localhost:8000/health

# Logs detalhados
docker-compose logs -f app-dev

# Reconstruir tudo
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up app-dev

# Limpeza completa
docker system prune -af
docker volume prune -f
```

## 📈 Otimizações Implementadas

### Docker

- **Multi-stage builds**: Reduz tamanho da imagem final
- **.dockerignore**: Otimização de contexto de build
- **Non-root user**: Segurança melhorada
- **Health checks**: Monitoramento automático

### CI/CD

- **Cache**: Cache de dependências Python e Docker layers
- **Parallel jobs**: Execução paralela de testes
- **Conditional deploys**: Deploy apenas em branches específicos
- **Multi-platform**: Build para x86_64 e ARM64

### Performance

- **Gunicorn**: WSGI server otimizado para produção
- **Worker processes**: Configuração automática baseada em CPU
- **Keep-alive**: Conexões persistentes
- **Static file serving**: Otimizado para arquivos estáticos

## 🔒 Segurança

### Container Security

- **Non-root user**: Execução com usuário não-privilegiado
- **Read-only filesystem**: Onde possível
- **Security scanning**: Scanning automático de vulnerabilidades
- **Minimal base image**: Python slim para reduzir superfície de ataque

### Application Security

- **Environment isolation**: Variáveis sensíveis via secrets
- **HTTPS ready**: Configuração para TLS/SSL
- **CORS**: Configuração de Cross-Origin Resource Sharing
- **Input validation**: Validação rigorosa de inputs

## 📚 Recursos Adicionais

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Python Security Guide](https://python-security.readthedocs.io/)

---

**Nota**: Este setup foi projetado para facilitar o desenvolvimento, testes automatizados e deploy seguro em produção. Todos os scripts incluem verificações de erro e rollback automático quando necessário.
