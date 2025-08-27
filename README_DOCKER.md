# AutoU Email Classifier

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Sistema inteligente de classificação de emails que combina IA (OpenAI GPT) com heurísticas para categorizar emails automaticamente.

## 🚀 Quick Start

### Usando Docker (Recomendado)

1. **Setup inicial**:
```bash
# Clonar e configurar
git clone <repository_url>
cd Processo_Seletivo

# Setup automático do ambiente
./scripts/dev-setup.sh
```

2. **Configurar variáveis de ambiente**:
```bash
# Editar .env e adicionar sua chave da OpenAI
nano .env
# Adicionar: OPENAI_API_KEY=sk-...
```

3. **Executar aplicação**:
```bash
# Desenvolvimento (com hot reload)
docker-compose up app-dev

# Produção
docker-compose up app
```

4. **Acessar aplicação**: http://localhost:8000

### Desenvolvimento Local

```bash
# Testes
./scripts/build-and-test.sh

# Testes com linting
./scripts/build-and-test.sh --lint

# Apenas linting
docker-compose --profile lint run --rm lint

# Apenas testes
docker-compose --profile test run --rm test
```

## 🏗️ Arquitetura

### Estrutura do Projeto
```
├── app/                    # Código da aplicação
│   ├── core/              # Configuração e logging
│   ├── services/          # Lógica de negócio (AI, NLP, Heurísticas)
│   ├── utils/             # Utilitários (PDF, TXT)
│   └── web/               # Rotas e templates
├── scripts/               # Scripts de automação
├── tests/                 # Testes automatizados
└── docker-compose.yml     # Orquestração de containers
```

### Componentes Principais

1. **AI Service** (`app/services/ai.py`)
   - Integração com OpenAI GPT-4o-mini
   - Fallback para heurísticas quando necessário
   - Sistema de cache e retry

2. **Heuristics Service** (`app/services/heuristics.py`)
   - Classificação baseada em palavras-chave
   - Backup quando AI não está disponível

3. **NLP Service** (`app/services/nlp.py`)
   - Processamento de texto com spaCy e NLTK
   - Análise de sentimento e entidades

4. **Web Interface** (`app/web/`)
   - Interface FastAPI com Jinja2
   - Upload de arquivos (PDF, TXT)
   - Dashboard de resultados

## 🐳 Docker & CI/CD

### Configuração Multi-stage

- **Development**: Ambiente completo com ferramentas de teste
- **Production**: Imagem otimizada apenas com dependências necessárias

### Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `./scripts/dev-setup.sh` | Configuração inicial do ambiente |
| `./scripts/build-and-test.sh` | Build e testes automatizados |
| `./scripts/deploy.sh` | Deploy em produção com rollback |

### Docker Compose Profiles

```bash
# Aplicação principal
docker-compose up app                    # Produção
docker-compose up app-dev                # Desenvolvimento

# Testes e qualidade
docker-compose --profile test run test   # Testes unitários
docker-compose --profile lint run lint   # Linting e formatação
```

## 🧪 Testes

### Execução de Testes

```bash
# Todos os testes (110 testes, 87% cobertura)
./scripts/build-and-test.sh

# Testes específicos
pytest tests/test_units.py -v
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v
```

### Status dos Testes

✅ **110/110 testes passando** (100% success rate)

### Breakdown por Categoria:
- ✅ **Units**: 35 testes - Lógica de negócio core
- ✅ **Integration**: 14 testes - Integração entre componentes  
- ✅ **Routes**: 11 testes - Endpoints da API
- ✅ **Utils**: 4 testes - Utilitários (PDF/TXT)
- ✅ **Requirements**: 17 testes - Validação de dependências
- ✅ **NLP**: 4 testes - Processamento de linguagem
- ✅ **Heuristics**: 2 testes - Lógica de fallback
- ✅ **Performance**: 11 testes - Benchmarks e limites
- ✅ **AI Improvements**: 12 testes - Melhorias de IA

### Cobertura de Testes

- **Total**: 87% de cobertura
- **110 testes** cobrindo todas as funcionalidades
- Relatórios HTML e XML gerados automaticamente

## 📊 Monitoramento

### Health Check
- **Endpoint**: `/health`
- **Status**: Verifica conectividade da API
- **Métricas**: Tempo de resposta e disponibilidade

### Logging
- **Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Formato**: JSON estruturado em produção
- **Rotação**: Configurada automaticamente

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# AI Configuration
USE_HEURISTIC_FALLBACK=true
CONFIDENCE_THRESHOLD=0.7
```

### Personalizando Classificação

1. **Palavras-chave Heurísticas**:
   - Edite as variáveis `HEURISTIC_KEYWORDS_*` no `.env`
   - Formato: palavras separadas por vírgula

2. **Prompts da IA**:
   - Modifique `app/services/prompt_templates.py`
   - Ajuste os prompts para seu domínio específico

3. **Limiares de Confiança**:
   - Configure `CONFIDENCE_THRESHOLD` (0.0-1.0)
   - Valores mais altos = classificações mais conservadoras

## 📁 Formatos Suportados

- **Texto**: `.txt` (UTF-8, Latin-1, CP1252)
- **PDF**: Extração automática de texto
- **Email**: Análise de assunto e conteúdo

### Saída
```json
{
  "category": "urgente",
  "confidence": 0.95,
  "method": "ai",
  "reasoning": "Email contém palavras indicativas de urgência...",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## 🚀 API Reference

### POST `/classify/text`
Classifica texto diretamente
```bash
curl -X POST http://localhost:8000/classify/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Preciso de ajuda urgente com o sistema"}'
```

### POST `/classify/file`
Classifica arquivo (TXT/PDF)
```bash
curl -X POST http://localhost:8000/classify/file \
  -F "file=@email.pdf"
```

### GET `/health`
Status da aplicação
```bash
curl http://localhost:8000/health
```

### GET `/docs`
Documentação interativa da API (Swagger UI)

## 🚀 Deploy em Produção

### Deploy Local

```bash
# Deploy automático com rollback
./scripts/deploy.sh

# Deploy personalizado
./scripts/deploy.sh --port 8080 --no-backup
```

### Deploy em Cloud

O projeto inclui configuração para:
- **Docker Hub**: Build automático de imagens
- **GitHub Actions**: CI/CD completo
- **Render/Heroku**: Deploy direto via `render.yaml`

### GitHub Actions CI/CD

Pipeline completo incluindo:
- Lint e formatação de código
- Testes unitários e integração
- Build de imagens Docker multi-plataforma
- Deploy automático
- Scanning de segurança

## 🔒 Segurança

### Implementações de Segurança

- **Container não-root**: Usuário dedicado (uid 1000)
- **Validação de input**: Sanitização rigorosa
- **Rate limiting**: Proteção contra abuso
- **Secrets**: Variáveis sensíveis via environment

### Scanning de Vulnerabilidades

```bash
# Verificação automática no CI/CD
# Manual:
docker scout quickview autou-classifier:production
```

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Erro de API Key**:
   ```bash
   # Verificar configuração
   grep OPENAI_API_KEY .env
   ```

2. **Container não inicia**:
   ```bash
   # Verificar logs
   docker logs autou-classifier-prod
   ```

3. **Testes falhando**:
   ```bash
   # Rebuild completo
   docker-compose down --volumes
   docker-compose build --no-cache
   ```

### Comandos Úteis

```bash
# Status dos containers
docker ps --filter name=autou-classifier

# Logs em tempo real
docker logs -f autou-classifier-prod

# Acesso ao container
docker exec -it autou-classifier-prod bash

# Limpeza completa
docker system prune -af
```

## 📈 Performance

### Benchmarks

- **Classificação simples**: ~2-5 segundos
- **Processamento PDF**: ~10-30 segundos
- **Throughput**: ~10-20 emails/minuto

### Otimizações

- **Cache**: Resultados de classificação em memória
- **Batch processing**: Múltiplos emails em paralelo
- **Fallback**: Heurísticas quando IA está lenta

### Limites Configurados
- **Tamanho máximo**: 2MB por arquivo
- **Caracteres**: 5.000 por texto
- **Timeout**: 30 segundos por classificação

## 🎯 Casos de Uso

### 1. Triagem de Emails Corporativos
```python
# Exemplo de integração
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/classify/text",
        json={"text": email_content}
    )
    classification = response.json()
    
    if classification["category"] == "urgente":
        # Escalar para equipe
        escalate_to_team(email_content)
```

### 2. Processamento em Lote
```bash
# Classificar múltiplos arquivos
for file in *.pdf; do
    curl -X POST http://localhost:8000/classify/file \
         -F "file=@$file" \
         >> results.jsonl
done
```

### 3. Dashboard de Monitoramento
Interface web fornece:
- Upload de arquivos
- Classificação em tempo real
- Histórico de classificações
- Métricas de confiança

## 🤝 Contribuição

### Setup de Desenvolvimento

1. Fork do repositório
2. `./scripts/dev-setup.sh`
3. Criar branch: `git checkout -b feature/nova-funcionalidade`
4. Desenvolver e testar: `./scripts/build-and-test.sh --lint`
5. Commit e push
6. Abrir Pull Request

### Padrões de Código

- **Formatação**: Black + isort
- **Linting**: flake8
- **Testes**: pytest com 85%+ cobertura
- **Commits**: Conventional Commits

## 📚 Recursos Adicionais

- [Documentação da API](http://localhost:8000/docs)
- [Cobertura de Testes](htmlcov/index.html)
- [Docker Setup](DOCKER_SETUP.md)
- [Melhorias de IA](AI_IMPROVEMENTS.md)

## 🚀 Roadmap & Melhorias

### Implementações Recentes ✅
- [x] Sistema de cache para otimização
- [x] Batch processing para múltiplos emails
- [x] Interface web melhorada
- [x] Métricas de confidence
- [x] Fallback robusto para heurísticas
- [x] Docker containerization completa
- [x] CI/CD pipeline com GitHub Actions
- [x] Scripts de automação para desenvolvimento

### Próximas Features 🔄
- [ ] Suporte a mais formatos (DOCX, MSG)
- [ ] API de feedback para aprendizado
- [ ] Dashboard analytics
- [ ] Integração com sistemas de email
- [ ] Modelo custom fine-tuned

## 📝 Licença

Este projeto foi desenvolvido para o processo seletivo da AutoU.

---

**Desenvolvido com ❤️ para AutoU** | **Status**: ✅ Pronto para Produção | **Docker**: ✅ Containerizado | **CI/CD**: ✅ GitHub Actions
