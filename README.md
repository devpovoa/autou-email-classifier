# AutoU - Classificador de E-mails

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Uma aplicação web inteligente para classificação automática de e-mails e geração de respostas, construída com **FastAPI**, **Tailwind CSS** e **Alpine.js**.

## 🚀 Demo

🔗 **[Link da aplicação em produção](https://autou-classificador.onrender.com)** *(será atualizado após deploy)*

## ✨ Funcionalidades

- **Classificação Inteligente**: Classifica e-mails como "Produtivo" ou "Improdutivo" usando IA + fallback heurístico
- **Geração de Respostas**: Cria respostas automáticas contextualizadas com diferentes tons (formal/neutro/amigável)
- **Upload de Arquivos**: Suporte para arquivos TXT e PDF (até 2MB)
- **Interface Premium**: Design moderno com Tailwind CSS, modo escuro e microinterações
- **Histórico Local**: Armazena os últimos 5 classificações no navegador
- **Métricas em Tempo Real**: Exibe latência, modelo utilizado e confiança
- **Acessibilidade**: Suporte completo a teclado e leitores de tela

## 🏗️ Arquitetura

### Stack Tecnológica
- **Backend**: FastAPI (Python 3.12) com Uvicorn
- **Frontend**: Jinja2 + TailwindCSS + Alpine.js
- **IA**: OpenAI GPT-4o-mini (configurável para HuggingFace)
- **Processamento**: spaCy + NLTK para NLP
- **Arquivos**: pypdf para extração de texto de PDFs
- **Deploy**: Render.com com Docker

### Estrutura do Projeto
```
app/
├── core/           # Configurações e logging
├── services/       # Lógica de negócio (IA, NLP, heurísticas)
├── utils/          # Utilitários para PDF/TXT
├── web/           # Rotas e templates
│   └── templates/  # Templates Jinja2
tests/             # Testes automatizados
main.py           # Ponto de entrada da aplicação
```

## 🛠️ Setup Local

### Pré-requisitos
- Python 3.12+
- pip
- Conta OpenAI (opcional, usa fallback heurístico)

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
PROVIDER=OpenAI
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini
PORT=8000
LOG_LEVEL=INFO
MAX_INPUT_CHARS=5000
```

5. **Execute a aplicação**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A aplicação estará disponível em: http://localhost:8000

## 🧪 Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio

# Executar todos os testes
python -m pytest tests/ -v

# Executar testes com cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

### Estrutura dos Testes
- `test_nlp.py`: Testa preprocessamento e extração de keywords
- `test_heuristics.py`: Testa classificação heurística
- `test_utils.py`: Testa extração de texto de arquivos
- `test_routes.py`: Testa endpoints da API

## 🚀 Deploy no Render

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

4. **Adicione variáveis de ambiente**
   ```
   PROVIDER=OpenAI
   OPENAI_API_KEY=sk-your-key-here
   MODEL_NAME=gpt-4o-mini
   PORT=8000
   ```

5. **Deploy**: O Render fará o build e deploy automaticamente

### Deploy Manual

1. **Instale o Render CLI**
```bash
npm install -g @render/cli
```

2. **Faça login**
```bash
render auth login
```

3. **Deploy**
```bash
render deploy
```

## 📊 Uso da API

### Endpoints Principais

#### `POST /classify`
Classifica e-mail e gera resposta
```bash
curl -X POST "http://localhost:8000/classify" \
  -F "text=Preciso de ajuda com erro no sistema" \
  -F "tone=neutro"
```

#### `POST /refine`
Refina resposta existente
```bash
curl -X POST "http://localhost:8000/refine" \
  -H "Content-Type: application/json" \
  -d '{"text":"Resposta atual", "tone":"formal"}'
```

#### `GET /health`
Verificação de saúde
```bash
curl http://localhost:8000/health
```

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

- **Validação de Entrada**: Limite de caracteres e tamanho de arquivo
- **Sanitização**: Remoção de informações sensíveis dos logs
- **Rate Limiting**: Controle de requisições por IP (em produção)
- **HTTPS**: Forçado em produção via Render
- **Secrets**: Variáveis de ambiente para chaves de API

## 🚧 Limitações Conhecidas

1. **Processamento de PDF**: Limitado a texto extraível (não OCR)
2. **Língua**: Otimizado para português brasileiro
3. **Contexto**: Não mantém histórico entre sessões
4. **Concorrência**: Uma classificação por vez por usuário

## 🔄 Próximos Passos

### Funcionalidades Planejadas
- [ ] Autenticação e contas de usuário
- [ ] Histórico persistente no servidor
- [ ] Suporte a múltiplos idiomas
- [ ] API REST completa com autenticação
- [ ] Dashboard administrativo
- [ ] Integração com sistemas de e-mail (IMAP/POP3)
- [ ] OCR para PDFs escaneados
- [ ] Treinamento de modelo personalizado

### Melhorias Técnicas
- [ ] Cache Redis para respostas frequentes
- [ ] Background tasks com Celery
- [ ] Métricas com Prometheus
- [ ] Testes de carga
- [ ] Pipeline CI/CD
- [ ] Backup automático de dados

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: add amazing feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para o processo seletivo AutoU**
