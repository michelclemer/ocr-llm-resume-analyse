# Makefile para Curriculum Analyzer API
# Comandos para facilitar o desenvolvimento e deployment

.PHONY: help install dev build up down test clean docs

# Variáveis
COMPOSE_FILE := docker-compose.yml
SERVICE_NAME := curriculum-analyzer
MONGODB_SERVICE := mongodb

# Configurações
PYTHON := python
UV := uv

help: ## Mostra esta mensagem de ajuda
	@echo "🎯 Curriculum Analyzer API - Comandos Disponíveis"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências locais
	@echo "📦 Instalando dependências..."
	$(UV) sync
	@echo "✅ Dependências instaladas!"

dev: ## Inicia desenvolvimento local (sem Docker)
	@echo "🚀 Iniciando em modo desenvolvimento..."
	$(PYTHON) main.py

dev-docker: ## Inicia com Docker Compose em modo desenvolvimento
	@echo "🐳 Iniciando com Docker (modo dev)..."
	docker-compose --profile dev up --build

build: ## Builda as imagens Docker
	@echo "🔨 Buildando imagens Docker..."
	docker-compose build
	@echo "✅ Build concluído!"

up: ## Inicia todos os serviços com Docker Compose
	@echo "🚀 Iniciando todos os serviços..."
	docker-compose up -d
	@echo "✅ Serviços iniciados!"
	@echo "📖 Swagger UI: http://localhost:8000/docs"
	@echo "🌐 API: http://localhost:8000"
	@echo "🗃️ MongoDB Express: http://localhost:8081"

down: ## Para todos os serviços
	@echo "⏹️ Parando serviços..."
	docker-compose down
	@echo "✅ Serviços parados!"

restart: down up ## Reinicia todos os serviços

logs: ## Mostra logs da aplicação
	docker-compose logs -f $(SERVICE_NAME)

logs-all: ## Mostra logs de todos os serviços
	docker-compose logs -f

status: ## Mostra status dos serviços
	@echo "📊 Status dos serviços:"
	docker-compose ps

health: ## Verifica saúde da API
	@echo "🏥 Verificando saúde da API..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ API não está respondendo"

test-api: ## Executa script de teste da API
	@echo "🧪 Executando testes da API..."
	$(PYTHON) test_api.py

test: install ## Executa testes unitários
	@echo "🧪 Executando testes unitários..."
	$(PYTHON) -m pytest tests/ -v || echo "⚠️ Testes não encontrados - crie em tests/"

clean: ## Limpa containers, volumes e imagens
	@echo "🧹 Limpando recursos Docker..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Limpeza concluída!"

clean-data: ## Remove dados do MongoDB (CUIDADO!)
	@echo "⚠️ ATENÇÃO: Isso irá remover TODOS os dados do MongoDB!"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	rm -rf ./data/mongodb
	@echo "🗑️ Dados removidos!"

backup-db: ## Faz backup do MongoDB
	@echo "💾 Fazendo backup do MongoDB..."
	mkdir -p ./backups
	docker exec $(SERVICE_NAME)-mongodb mongodump --out /data/backup
	docker cp $(SERVICE_NAME)-mongodb:/data/backup ./backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "✅ Backup salvo em ./backups/"

restore-db: ## Restaura backup do MongoDB (especifique BACKUP_DIR=path)
	@echo "📥 Restaurando backup do MongoDB..."
	@if [ -z "$(BACKUP_DIR)" ]; then echo "❌ Especifique BACKUP_DIR=path"; exit 1; fi
	docker cp $(BACKUP_DIR) $(SERVICE_NAME)-mongodb:/data/restore
	docker exec $(SERVICE_NAME)-mongodb mongorestore /data/restore
	@echo "✅ Backup restaurado!"

docs: ## Abre documentação da API
	@echo "📖 Abrindo documentação da API..."
	@command -v xdg-open >/dev/null && xdg-open http://localhost:8000/docs || \
	 command -v open >/dev/null && open http://localhost:8000/docs || \
	 echo "📖 Acesse: http://localhost:8000/docs"

shell-api: ## Acessa shell do container da API
	docker exec -it $(SERVICE_NAME)-api /bin/bash

shell-db: ## Acessa shell do MongoDB
	docker exec -it $(SERVICE_NAME)-mongodb mongosh curriculum_analyzer

env-setup: ## Cria arquivo .env a partir do exemplo
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Arquivo .env criado! Configure as variáveis necessárias."; \
	else \
		echo "⚠️ Arquivo .env já existe!"; \
	fi

check-deps: ## Verifica se todas as dependências estão instaladas
	@echo "🔍 Verificando dependências do sistema..."
	@command -v docker >/dev/null || echo "❌ Docker não encontrado"
	@command -v docker-compose >/dev/null || echo "❌ Docker Compose não encontrado"
	@command -v $(UV) >/dev/null || echo "❌ UV não encontrado"
	@command -v $(PYTHON) >/dev/null || echo "❌ Python não encontrado"
	@echo "✅ Verificação concluída!"

quick-start: env-setup build up health ## Setup completo e início rápido
	@echo "🎉 Curriculum Analyzer iniciado com sucesso!"
	@echo ""
	@echo "📖 Próximos passos:"
	@echo "   1. Acesse a documentação: http://localhost:8000/docs"
	@echo "   2. Teste a API: make test-api"
	@echo "   3. Veja os logs: make logs"

demo: ## Executa demonstração completa
	@echo "🎬 Executando demonstração da API..."
	$(PYTHON) test_api.py

# Comandos de desenvolvimento
dev-install: ## Instala dependências de desenvolvimento
	$(UV) add --dev pytest pytest-asyncio httpx black flake8 mypy

format: ## Formata código com black
	black .

lint: ## Verifica código com flake8
	flake8 .

type-check: ## Verifica tipos com mypy
	mypy .

# Comandos de produção
prod-build: ## Build para produção
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Inicia em modo produção
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Informações
info: ## Mostra informações do sistema
	@echo "🎯 Curriculum Analyzer API - Informações do Sistema"
	@echo "=================================================="
	@echo "📁 Diretório atual: $(PWD)"
	@echo "🐳 Docker version: $$(docker --version)"
	@echo "🐙 Docker Compose: $$(docker-compose --version)"
	@echo "🐍 Python: $$($(PYTHON) --version)"
	@echo "📦 UV: $$($(UV) --version)"
	@echo ""
	@echo "🌐 URLs importantes:"
	@echo "   API: http://localhost:8000"
	@echo "   Docs: http://localhost:8000/docs"
	@echo "   Health: http://localhost:8000/health"
	@echo "   MongoDB Express: http://localhost:8081"

# Por padrão, mostra ajuda
.DEFAULT_GOAL := help