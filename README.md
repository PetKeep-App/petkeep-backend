# PetKeep Backend

Backend do aplicativo PetKeep - Plataforma para PetSitters.

## Tecnologias

- Django 5.0
- Django REST Framework
- PostgreSQL

## Configuração do Ambiente

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
# Edite o arquivo .env com suas configurações
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

## Estrutura do Projeto

```
petkeep-backend/
├── config/          # Configurações do projeto Django
├── apps/            # Aplicativos Django
├── requirements.txt # Dependências de produção
├── requirements-dev.txt # Dependências de desenvolvimento
└── manage.py
```

## Comandos Úteis

### Criar nova app
```bash
python manage.py startapp nome_da_app apps/nome_da_app
```

### Criar migrações
```bash
python manage.py makemigrations
```

### Executar testes
```bash
pytest
```

### Formatação de código
```bash
black .
isort .
flake8
```
