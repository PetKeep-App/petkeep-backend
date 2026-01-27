# PetKeep Backend

Backend do aplicativo PetKeep - Plataforma para PetSitters.

## Tecnologias

- Django 5.0
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose

## 🐳 Início Rápido com Docker (Recomendado)

### Pré-requisitos
- Docker
- Docker Compose

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
# O arquivo já vem configurado para Docker
```

### 2. Construir e iniciar os serviços

```bash
make build
make up
```

### 3. Criar superusuário

```bash
make createsuperuser
```

### 4. Acessar a aplicação

- API: http://localhost:8080
- Admin: http://localhost:8080/admin/
- Swagger Docs: http://localhost:8080/api/docs/
- ReDoc: http://localhost:8080/api/redoc/

### Comandos Make Disponíveis

```bash
make help              # Lista todos os comandos disponíveis
make build             # Constrói as imagens Docker
make up                # Inicia os containers
make down              # Para os containers
make restart           # Reinicia os containers
make logs              # Exibe logs do backend
make ps                # Status dos containers

# Comandos Django
make migrate           # Executa migrações
make makemigrations    # Cria novas migrações
make shell             # Abre Django shell
make createsuperuser   # Cria superusuário
make test              # Executa testes

# Utilitários
make exec              # Abre bash no container
make exec-db           # Abre psql no banco
make clean             # Remove tudo (containers, volumes, imagens)
```

### Comandos Docker Alternativos

```bash
# Parar os serviços
docker-compose down

# Ver logs
docker-compose logs -f backend

# Executar comandos Django
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py shell

# Rebuild após mudanças
docker-compose up --build

# Limpar tudo (cuidado: remove volumes)
docker-compose down -v
```

---

## 💻 Desenvolvimento Local (Sem Docker)

### 1. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements-dev.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Altere DB_HOST=db para DB_HOST=localhost
# Ou use SQLite alterando DB_ENGINE=django.db.backends.sqlite3 e DB_NAME=db.sqlite3
```

### 4. Executar migrações

```bash
python manage.py migrate
```

### 5. Criar superusuário

```bash
python manage.py createsuperuser
```

### 6. Executar servidor

```bash
python manage.py runserver
```

---

## Estrutura do Projeto

```
petkeep-backend/
├── config/              # Configurações do projeto Django
├── apps/                # Aplicativos Django
├── nginx/               # Configuração Nginx (produção)
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração Docker (desenvolvimento)
├── docker-compose.prod.yml  # Orquestração Docker (produção)
├── docker-entrypoint.sh # Script de inicialização Docker
├── requirements.txt     # Dependências de produção
├── requirements-dev.txt # Dependências de desenvolvimento
├── requirements-prod.txt # Dependências extras para produção
└── manage.py
```

## 🚀 Deploy em Produção

Para produção, use o `docker-compose.prod.yml` que inclui Nginx e Gunicorn:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Comandos Úteis

### Criar nova app
```bash
# Com Docker
docker-compose exec backend python manage.py startapp nome_da_app apps/nome_da_app

# Sem Docker
python manage.py startapp nome_da_app apps/nome_da_app
```

### Criar migrações
```bash
# Com Docker
docker-compose exec backend python manage.py makemigrations

# Sem Docker
python manage.py makemigrations
```

### Executar testes
```bash
# Com Docker
docker-compose exec backend pytest

# Sem Docker
pytest
```

### Formatação de código
```bash
black .
isort .
flake8
```
