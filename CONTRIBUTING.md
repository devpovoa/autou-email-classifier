# Contributing to AutoU Email Classifier

Obrigado pelo seu interesse em contribuir com o projeto **AutoU Email Classifier**!
Este documento descreve diretrizes de contribuição e boas práticas.
👉 Para overview rápido do projeto, consulte o [README.md](README.md).

---

## 🚀 Getting Started

### Pré-requisitos
- Python 3.12+
- Docker e Docker Compose
- Git

### Setup do Ambiente
```bash
git clone <repository_url>
cd autou-email-classifier
./scripts/dev-setup.sh
cp .env.example .env   # Configure variáveis
docker compose up app-dev
````

---

## 📋 Padrões de Desenvolvimento

### Git Workflow

* `main`: produção
* `develop`: integração
* `feature/*`: novas funcionalidades
* `bugfix/*`: correções
* `hotfix/*`: correções urgentes

### Commits Convencionais

* `feat`: Nova funcionalidade
* `fix`: Correção de bug
* `docs`: Documentação
* `style`: Formatação sem impacto funcional
* `refactor`: Refatoração
* `test`: Testes
* `chore`: Tarefas de manutenção
* `ci`: Configurações de CI/CD
* `perf`: Melhorias de performance

Exemplos:

```bash
git commit -m "feat(api): add email batch classification endpoint"
git commit -m "fix(docker): resolve container startup timeout issue"
```

---

## 🧪 Testes

* **Cobertura mínima:** não reduzir cobertura atual (58%); idealmente aumentar.
* **Testes unitários:** lógica de negócio.
* **Testes de integração:** APIs.
* **Mocks** para dependências externas.

```bash
# Todos os testes
pytest -v

# Com cobertura
pytest --cov=app --cov-report=html
```

---

## ⚡ Performance

Benchmarks esperados:

* Classificação simples: **< 2s**
* Upload PDF: **< 30s**
* Startup: **< 30s**
* Memory usage: **< 512MB**

---

## 🔒 Segurança

* Nunca commite secrets
* Valide todos inputs
* Dependências atualizadas
* Containers não-root

---

## 🚀 Release Process

* Semantic Versioning: `MAJOR.MINOR.PATCH`
* Tags Git (`git tag v1.0.0 && git push origin v1.0.0`)
* CI/CD via GitHub Actions cuida do deploy

---

## 📄 Licença

Ao contribuir, você concorda que suas alterações serão licenciadas sob a **MIT License**.
