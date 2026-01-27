.PHONY: help build up down restart logs migrate makemigrations shell createsuperuser test clean ps

# Variáveis
DOCKER_COMPOSE = docker-compose
BACKEND_CONTAINER = petkeep_backend
DB_CONTAINER = petkeep_db

help:
	@echo "Comandos disponíveis para o PetKeep Backend:"
	@echo ""
	@echo "  make build          - Constrói as imagens Docker"
	@echo "  make up             - Inicia os containers em background"
	@echo "  make down           - Para e remove os containers"
	@echo "  make restart        - Reinicia os containers"
	@echo "  make logs           - Exibe os logs do backend"
	@echo "  make logs-db        - Exibe os logs do banco de dados"
	@echo "  make ps             - Lista os containers em execução"
	@echo ""
	@echo "  make migrate        - Executa as migrações do Django"
	@echo "  make makemigrations - Cria novas migrações"
	@echo "  make shell          - Abre o shell do Django"
	@echo "  make createsuperuser - Cria um superusuário"
	@echo ""
	@echo "  make test           - Executa os testes"
	@echo "  make clean          - Remove containers, volumes e imagens"
	@echo "  make collectstatic  - Coleta arquivos estáticos"

build:
	@echo "🏗️  Construindo as imagens Docker..."
	$(DOCKER_COMPOSE) build

up:
	@echo "🚀 Iniciando os containers..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Containers iniciados! Backend disponível em http://localhost:8080"

down:
	@echo "🛑 Parando os containers..."
	$(DOCKER_COMPOSE) down

restart: down up

logs:
	@echo "📋 Logs do backend:"
	$(DOCKER_COMPOSE) logs -f backend

logs-db:
	@echo "📋 Logs do banco de dados:"
	$(DOCKER_COMPOSE) logs -f db

ps:
	@echo "📊 Status dos containers:"
	$(DOCKER_COMPOSE) ps

migrate:
	@echo "🔄 Executando migrações..."
	$(DOCKER_COMPOSE) exec backend python manage.py migrate

makemigrations:
	@echo "📝 Criando migrações..."
	$(DOCKER_COMPOSE) exec backend python manage.py makemigrations

shell:
	@echo "🐚 Abrindo Django shell..."
	$(DOCKER_COMPOSE) exec backend python manage.py shell

createsuperuser:
	@echo "👤 Criando superusuário..."
	$(DOCKER_COMPOSE) exec backend python manage.py createsuperuser

collectstatic:
	@echo "📦 Coletando arquivos estáticos..."
	$(DOCKER_COMPOSE) exec backend python manage.py collectstatic --noinput

test:
	@echo "🧪 Executando testes..."
	$(DOCKER_COMPOSE) exec backend pytest

clean:
	@echo "🧹 Limpando containers, volumes e imagens..."
	$(DOCKER_COMPOSE) down -v --rmi all
	@echo "✅ Limpeza concluída!"

# Comandos adicionais úteis
exec:
	@echo "💻 Abrindo bash no container backend..."
	$(DOCKER_COMPOSE) exec backend bash

exec-db:
	@echo "💻 Abrindo psql no container db..."
	$(DOCKER_COMPOSE) exec db psql -U petkeep_user -d petkeep_db

requirements:
	@echo "📦 Instalando dependências..."
	$(DOCKER_COMPOSE) exec backend pip install -r requirements.txt

rebuild: down build up
	@echo "✅ Rebuild completo!"
