#!/bin/bash
# Script para executar suíte completa de testes do AutoU

echo "🧪 Iniciando Suíte de Testes - AutoU Classificador de E-mails"
echo "============================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para executar testes e mostrar resultado
run_tests() {
    local test_name="$1"
    local test_path="$2"
    local additional_args="$3"
    
    echo -e "\n${BLUE}📋 Executando: $test_name${NC}"
    echo "----------------------------------------"
    
    if python -m pytest "$test_path" $additional_args; then
        echo -e "${GREEN}✅ $test_name - PASSOU${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name - FALHOU${NC}"
        return 1
    fi
}

# Verificar se pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest não encontrado. Instalando...${NC}"
    pip install pytest pytest-asyncio pytest-cov
fi

# Contador de resultados
total_tests=0
passed_tests=0

# 1. Testes de Unidade
echo -e "${YELLOW}🔧 TESTES UNITÁRIOS${NC}"
if run_tests "Testes Unitários" "tests/test_units.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

if run_tests "Testes NLP" "tests/test_nlp.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

if run_tests "Testes Heurísticas" "tests/test_heuristics.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

if run_tests "Testes Utilitários" "tests/test_utils.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

# 2. Testes de Integração  
echo -e "\n${YELLOW}🔗 TESTES DE INTEGRAÇÃO${NC}"
if run_tests "Testes de Integração" "tests/test_integration.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

if run_tests "Testes de Rotas" "tests/test_routes.py" "-v"; then
    ((passed_tests++))
fi
((total_tests++))

# 3. Testes de Performance (opcional)
echo -e "\n${YELLOW}⚡ TESTES DE PERFORMANCE${NC}"
echo "Executando testes de performance (podem demorar)..."
if run_tests "Testes de Performance" "tests/test_performance.py" "-v --tb=short"; then
    ((passed_tests++))
fi
((total_tests++))

# 4. Testes com Coverage (se disponível)
echo -e "\n${YELLOW}📊 COBERTURA DE CÓDIGO${NC}"
if command -v pytest-cov &> /dev/null; then
    echo "Gerando relatório de cobertura..."
    python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --tb=short
    echo -e "${BLUE}📁 Relatório HTML salvo em: htmlcov/index.html${NC}"
fi

# Resumo final
echo -e "\n${BLUE}📈 RESUMO FINAL${NC}"
echo "============================================================"
echo -e "Total de suítes executadas: $total_tests"
echo -e "Suítes que passaram: $passed_tests"
echo -e "Suítes que falharam: $((total_tests - passed_tests))"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "\n${GREEN}🎉 TODOS OS TESTES PASSARAM!${NC}"
    echo -e "${GREEN}✨ Sistema pronto para produção${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  ALGUNS TESTES FALHARAM${NC}"
    echo -e "${YELLOW}🔍 Verifique os logs acima para detalhes${NC}"
    echo -e "\n${BLUE}💡 Dicas para resolver falhas comuns:${NC}"
    echo "1. Instalar dependências: pip install -r requirements.txt"
    echo "2. Configurar variáveis de ambiente (.env)"
    echo "3. Verificar se todas as importações estão corretas"
    echo "4. Executar testes individualmente para debug"
    exit 1
fi
