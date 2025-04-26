#!/bin/bash

# Cores para facilitar a leitura
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando testes do FleetSecure...${NC}"

# Executa os testes com pytest e cobertura
python -m pytest --cov=. --cov-report=html --cov-report=term -v $@

# Verifica o código de saída do pytest
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Todos os testes passaram com sucesso!${NC}"
else
    echo -e "\n${RED}Alguns testes falharam. Verifique os erros acima.${NC}"
fi

echo -e "\n${YELLOW}Relatório de cobertura gerado em htmlcov/index.html${NC}"
echo -e "Para visualizar, abra o arquivo no seu navegador." 