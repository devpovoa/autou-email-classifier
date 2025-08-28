# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-26

### Added

#### Core Features
- Email classification system combining AI (OpenAI GPT-4o-mini) with heuristic fallback
- Web interface with drag-and-drop file upload functionality
- RESTful API with comprehensive OpenAPI documentation
- Support for PDF and TXT file processing
- Two classification categories: **Produtivo** and **Improdutivo**

#### AI & NLP
- OpenAI GPT-4o-mini integration with configurable models
- Heuristic classification based on keyword matching
- NLP preprocessing with spaCy and NLTK
- Confidence scoring for classification results
- Automatic fallback to heuristics when AI is unavailable

#### Infrastructure
- Docker multi-stage builds (development and production)
- Docker Compose orchestration with service profiles
- GitHub Actions CI/CD pipeline with automated testing
- Comprehensive test suite (62 tests, 58% coverage)
- Production deployment scripts with rollback capability

#### Developer Experience
- Automated development environment setup (`dev-setup.sh`)
- Code quality enforcement (Black, isort, flake8)
- Pre-commit hooks for code quality validation
- Comprehensive documentation and contribution guidelines
- Performance benchmarking and monitoring

### Security
- Container running as non-root user
- Input validation and sanitization
- Environment variable configuration for secrets
- Security scanning in CI/CD pipeline

### Technical Specifications
- **Python**: 3.12+
- **Framework**: FastAPI with Jinja2 templates
- **AI Provider**: OpenAI GPT-4o-mini (with Hugging Face fallback)
- **Database**: File-based (no persistent storage)
- **Container**: Multi-stage Docker builds
- **Testing**: pytest with 58% code coverage
- **Deployment**: Docker Compose + production scripts

### Performance Metrics
- Classification response time: < 2 seconds
- PDF processing time: 10–30 seconds (depending on size)
- Application startup time: < 30 seconds
- Memory usage: < 512MB in production
- File size limit: 2MB maximum
- Concurrent requests: Configurable workers
- Classification accuracy: ~90%

### API Endpoints
- `GET /` - Web interface
- `POST /api/classify/text` - Text classification
- `POST /api/classify/file` - File upload and classification
- `POST /refine` - Refine generated reply
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

### Docker Services
- `app` - Production application
- `app-dev` - Development with hot reload
- `test` - Test runner (profile: test)
- `lint` - Code quality checks (profile: lint)

### Scripts
- `./scripts/dev-setup.sh` - Complete development environment setup
- `./scripts/build-and-test.sh` - Build images and run tests
- `./scripts/deploy.sh` - Production deployment with rollback

### Documentation
- `README.md` - Main project documentation
- `DOCKER_SETUP.md` - Docker configuration guide
- `CONTRIBUTING.md` - Development workflow and standards
- `AI_IMPROVEMENTS.md` - AI service enhancements
- `TESTS_README.md` - Testing documentation

[1.0.0]: https://github.com/autou/email-classifier/releases/tag/v1.0.0
