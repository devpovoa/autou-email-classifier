# AutoU - Classificador de E-mails

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Coverage](https://img.shields.io/badge/Coverage-87%25-brightgreen.svg)
![Tests](https://img.shields.io/badge/Tests-179%20passed-success.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

Uma aplicação web inteligente para classificação automática de e-mails e geração de respostas, construída com **FastAPI**, **Tailwind CSS** e **Alpine.js**.

> **🎯 Status**: Sistema completo com autenticação JWT, 87% cobertura de testes, containerização Docker e deploy automatizado.

## 🚀 Demo

🔗 **[Link da aplicação em produção](https://autou-classificador.onrender.com)** *(será atualizado após deploy)*

## ✨ Funcionalidades

- **🧠 Classificação Inteligente**: Classifica e-mails como "Produtivo" ou "Improdutivo" usando IA + fallback heurístico
- **✍️ Geração de Respostas**: Cria respostas automáticas contextualizadas com diferentes tons (formal/neutro/amigável)
- **📁 Upload de Arquivos**: Suporte para arquivos TXT e PDF (até 2MB)
- **🎨 Interface Premium**: Design moderno com Tailwind CSS, modo escuro e microinterações
- **📊 Histórico Local**: Armazena os últimos 5 classificações no navegador
- **⚡ Métricas em Tempo Real**: Exibe latência, modelo utilizado e confiança
- **♿ Acessibilidade**: Suporte completo a teclado e leitores de tela
- **🔐 Segurança JWT**: Sistema completo de autenticação e autorização
- **🐳 Docker Ready**: Containerização completa para produção

## 📚 Documentação Complementar

### 📋 Guias Essenciais
- 🐳 **[Setup Docker](README_DOCKER.md)** - Instruções completas de containerização e deploy
- 🔒 **[Guia de Segurança](API_SECURITY_GUIDE.md)** - Implementação JWT e boas práticas de API
- 🧪 **[Documentação de Testes](TESTS_README.md)** - Guia completo de testes e cobertura
- 🤝 **[Como Contribuir](CONTRIBUTING.md)** - Guia para desenvolvedores e colaboradores

### 📖 Documentação Técnica
- 🚀 **[Melhorias da IA](AI_IMPROVEMENTS.md)** - Otimizações e engenharia de prompts
- 🔑 **[Implementação JWT](JWT_IMPLEMENTATION_SUMMARY.md)** - Resumo da autenticação
- 🐋 **[Docker Setup](DOCKER_SETUP.md)** - Configuração detalhada de containers
- 📋 **[Changelog](CHANGELOG.md)** - Histórico de versões e mudanças
- ✅ **[Validação Final](FINAL_VALIDATION.md)** - Relatório de testes e validação

## 🏗️ Arquitetura

### Stack Tecnológica
- **Backend**: FastAPI (Python 3.12) com Uvicorn ASGI
- **Frontend**: Jinja2 + TailwindCSS + Alpine.js
- **Autenticação**: JWT com python-jose e passlib
- **IA**: OpenAI GPT-4o-mini (configurável para HuggingFace)
- **Processamento**: spaCy + NLTK para análise de linguagem natural
- **Arquivos**: pypdf para extração de texto de PDFs
- **Deploy**: Render.com com Docker multi-stage
- **Testes**: pytest com 87% de cobertura

### Estrutura do Projeto
```
app/
├── core/           # 🔧 Configurações, auth JWT e logging
├── services/       # 🧠 Lógica de negócio (IA, NLP, heurísticas)
├── utils/          # 🛠️ Utilitários para PDF/TXT
├── web/           # 🌐 Rotas FastAPI e templates
│   └── templates/  # 📄 Templates Jinja2 com Alpine.js
tests/             # 🧪 Suite de testes (87% cobertura)
scripts/           # 📜 Scripts de automação e deploy
main.py           # 🚀 Ponto de entrada da aplicação
```

> **📊 Métricas do Projeto**: 179 testes | 87% cobertura | Docker ready | JWT implementado

## 🛠️ Setup Local

> **🚀 Quick Start**: Para setup com Docker, veja o **[README_DOCKER.md](README_DOCKER.md)** com instruções automatizadas.

### Pré-requisitos
- Python 3.12+
- pip ou poetry
- Conta OpenAI (opcional - sistema funciona com fallback heurístico)
- Git

### Instalação

1. **Clone o repositório**
```bash
git clone <repo-url>
cd Processo_Seletivo
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```env
# API Configuration
PROVIDER=OpenAI
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini

# Server Configuration
PORT=8000
LOG_LEVEL=INFO
MAX_INPUT_CHARS=5000
MAX_FILE_SIZE=2097152

# JWT Configuration (gerado automaticamente se não definido)
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default API Authentication
DEFAULT_API_KEY=your-api-key-here
```

5. **Execute a aplicação**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A aplicação estará disponível em: http://localhost:8000

> **🔐 Autenticação**: Use `admin`/`admin123` para login ou configure suas próprias credenciais.

## 🧪 Executar Testes

> **📖 Documentação Completa**: Veja **[TESTS_README.md](TESTS_README.md)** para guia detalhado de testes.

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio pytest-cov

# Executar todos os testes
python -m pytest tests/ -v

# Executar testes com cobertura
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Executar testes específicos
python -m pytest tests/test_auth.py -v    # Testes JWT
python -m pytest tests/test_routes.py -v  # Testes de rotas
```

### 📊 Cobertura Atual: 87%
- **179 testes** executados com sucesso
- **Auth/JWT**: 92% de cobertura  
- **Services**: 85-97% de cobertura
- **Routes**: 79% de cobertura

### Estrutura dos Testes
- `test_auth.py`: Sistema JWT e autenticação
- `test_routes.py`: Endpoints da API web
- `test_integration.py`: Testes de fluxo completo
- `test_nlp.py`: Processamento de linguagem natural
- `test_heuristics.py`: Sistema de classificação heurística
- `test_utils.py`: Utilitários de arquivos PDF/TXT

## 🚀 Deploy no Render

> **🐳 Deploy com Docker**: Para instruções completas de containerização, veja **[README_DOCKER.md](README_DOCKER.md)**.

### Deploy Automático (Recomendado)

1. **Fork este repositório**

2. **Conecte ao Render**
   - Acesse [render.com](https://render.com)
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub

3. **Configure o serviço**
   - Nome: `autou-classificador`
   - Runtime: `Docker`
   - Branch: `main`
   - Build Command: `docker build -t app .`
   - Start Command: `docker run -p $PORT:$PORT app`

4. **Adicione variáveis de ambiente**
   ```
   PROVIDER=OpenAI
   OPENAI_API_KEY=sk-your-key-here
   MODEL_NAME=gpt-4o-mini
   PORT=8000
   JWT_SECRET_KEY=your-production-secret
   DEFAULT_API_KEY=your-production-api-key
   ```

5. **Deploy**: O Render fará o build e deploy automaticamente

> **⚠️ Importante**: Configure todas as variáveis de ambiente obrigatórias antes do deploy.

### Deploy Manual

```bash
# Instale o Render CLI
npm install -g @render/cli

# Faça login
render auth login

# Deploy
render deploy
```

## 📊 Uso da API

> **🔒 Guia de Segurança**: Para detalhes sobre autenticação JWT e segurança da API, veja **[API_SECURITY_GUIDE.md](API_SECURITY_GUIDE.md)**.

### Autenticação

A API possui endpoints públicos e protegidos:

```bash
# Login para obter token JWT
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Endpoints Principais

#### `POST /classify` (Público)
Classifica e-mail e gera resposta
```bash
curl -X POST "http://localhost:8000/classify" \
  -F "text=Preciso de ajuda com erro no sistema" \
  -F "tone=neutro"
```

#### `POST /api/classify` (Protegido)
API endpoint com autenticação
```bash
curl -X POST "http://localhost:8000/api/classify" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Preciso de ajuda urgente", "tone":"formal"}'
```

#### `POST /refine` (Público)
Refina resposta existente
```bash
curl -X POST "http://localhost:8000/refine" \
  -H "Content-Type: application/json" \
  -d '{"text":"Resposta atual", "tone":"formal"}'
```

#### `GET /health` (Público)
Verificação de saúde do sistema
```bash
curl http://localhost:8000/health
```

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Decisões Técnicas

### Por que FastAPI?
- Performance superior ao Flask
- Documentação automática (OpenAPI)
- Suporte nativo a async/await
- Validação automática com Pydantic

### Por que SSR com Jinja2?
- Menor complexidade que SPAs
- SEO-friendly
- Carregamento inicial mais rápido
- Ideal para aplicações focadas em funcionalidade

### Por que Fallback Heurístico?
- Garante funcionamento mesmo sem API externa
- Reduz custos operacionais
- Melhora confiabilidade do sistema

### Por que Tailwind + Alpine.js?
- Bundle pequeno e performance otimizada
- Desenvolvimento rápido com classes utilitárias
- Reatividade simples sem complexidade de frameworks

## 📈 Métricas e Monitoramento

A aplicação registra automaticamente:
- **Latência**: Tempo de resposta de cada classificação
- **Uso de Tokens**: Consumo da API OpenAI
- **Taxa de Fallback**: Quando heurísticas são utilizadas
- **Erros**: Falhas de classificação ou processamento

Logs em formato JSON estruturado para fácil integração com ferramentas de monitoramento.

## 🔒 Segurança

> **🛡️ Guia Detalhado**: Para informações completas sobre segurança, veja **[API_SECURITY_GUIDE.md](API_SECURITY_GUIDE.md)**.

- **🔐 Autenticação JWT**: Sistema completo com tokens seguros
- **✅ Validação de Entrada**: Limite de caracteres e tamanho de arquivo
- **🧹 Sanitização**: Remoção de informações sensíveis dos logs
- **⏱️ Rate Limiting**: Controle de requisições por IP (produção)
- **🔒 HTTPS**: Forçado em produção via Render
- **🔑 Secrets Management**: Variáveis de ambiente para chaves de API
- **🛡️ CORS**: Configuração adequada para produção
- **📝 Logs Estruturados**: Auditoria completa de ações

## 🚧 Limitações Conhecidas

1. **Processamento de PDF**: Limitado a texto extraível (não OCR)
2. **Língua**: Otimizado para português brasileiro
3. **Contexto**: Não mantém histórico entre sessões
4. **Concorrência**: Uma classificação por vez por usuário

## 🔄 Próximos Passos

### ✅ Funcionalidades Já Implementadas
- [x] **Autenticação JWT** - Sistema completo com tokens seguros
- [x] **API REST com autenticação** - Endpoints `/api/classify/*` protegidos
- [x] **Testes de carga** - Suite de testes de performance implementada
- [x] **Pipeline CI/CD** - GitHub Actions configurado
- [x] **Logs estruturados** - Sistema de logging JSON implementado
- [x] **Documentação OpenAPI** - Swagger/ReDoc disponíveis
- [x] **Containerização Docker** - Multi-stage build otimizado

### 🚧 Funcionalidades Planejadas
- [ ] **Histórico persistente no servidor** (atualmente apenas local)
- [ ] **Suporte a múltiplos idiomas** (otimizado para português)
- [ ] **Dashboard administrativo** com métricas avançadas
- [ ] **Integração com sistemas de e-mail** (IMAP/POP3)
- [ ] **OCR para PDFs escaneados** (apenas texto extraível)
- [ ] **Treinamento de modelo personalizado**
- [ ] **Sistema de usuários múltiplos** (atualmente admin único)

### 🔧 Melhorias Técnicas Planejadas
- [ ] **Cache Redis** para respostas frequentes
- [ ] **Background tasks** com Celery para processamento assíncrono
- [ ] **Métricas com Prometheus** e Grafana
- [ ] **Backup automático** de dados e configurações
- [ ] **Rate limiting** mais avançado por usuário
- [ ] **Health checks** mais detalhados
- [ ] **Monitoramento APM** (Application Performance Monitoring)

## 🤝 Contribuição

> **📋 Guia Completo**: Veja **[CONTRIBUTING.md](CONTRIBUTING.md)** para instruções detalhadas.

### Como Contribuir

1. **Fork o projeto**
2. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit suas mudanças** (`git commit -m 'feat: add amazing feature'`)
4. **Push para a branch** (`git push origin feature/AmazingFeature`)
5. **Abra um Pull Request**

### Diretrizes
- 📝 Siga os padrões de commit convencionais
- 🧪 Mantenha a cobertura de testes acima de 85%
- 📖 Documente novas funcionalidades
- 🎨 Use formatação com black e isort
- ✅ Execute todos os testes antes do PR

## 📋 Changelog

Veja **[CHANGELOG.md](CHANGELOG.md)** para histórico completo de versões e mudanças.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para o processo seletivo AutoU**
