# QuantMind Engine

Este projeto conecta-se a um banco PostgreSQL para armazenar carteiras otimizadas.

Pré-requisitos
- PostgreSQL instalado e acessível (ex.: `localhost:5432`)
- Python 3.10+ e virtualenv

Instalação rápida

Windows PowerShell:

```powershell
# ativar venv (se já criado)
venv\Scripts\Activate.ps1

# instalar dependências
pip install -r requirements.txt

# copiar/editar .env com suas credenciais
type .env

# rodar pipeline
venv\Scripts\python.exe main.py
```

Criando o banco e usuário PostgreSQL (opcional — o código tenta criar o DB automaticamente):

1) Usando `psql` como superuser (psql deve estar no PATH):

```sql
-- conectar como superuser (p.ex. postgres)
psql -U postgres

-- dentro do psql:
CREATE USER quantmind_user WITH PASSWORD 'senha_segura';
CREATE DATABASE quantmind_db OWNER quantmind_user;
GRANT ALL PRIVILEGES ON DATABASE quantmind_db TO quantmind_user;
\q
```

2) Atualize seu arquivo `.env` com as credenciais:

```
DB_HOST=localhost
DB_NAME=quantmind_db
DB_USER=quantmind_user
DB_PASS=sua_senha_aqui
DB_PORT=5432
```

Observações
- O `PostgresConnector` tenta usar `psycopg2` e faz fallback para `pg8000` se houver problemas de ambiente.
- O script `database/setup_db.sql` é executado automaticamente por `main.py` na primeira execução.

Se quiser, eu atualizo o `requirements.txt` com versões específicas ou adiciono instruções para Docker/postgres local.

Usando Docker (opcional)

1) Para levantar um PostgreSQL local com Docker Compose:

```powershell
docker-compose up -d
```

2) Verifique se o banco está ativo (porta 5432):

```powershell
docker ps
```

3) O `docker-compose.yml` incluído cria o banco `quantmind_db` com usuário `postgres` e senha `251025`. Você pode alterar essas configurações no arquivo.

Listar carteiras e ativos

Criei um script helper em `scripts/list_portfolios.py` que imprime todas as carteiras e seus ativos vinculados.

Execução (no venv):

```powershell
venv\Scripts\Activate.ps1
venv\Scripts\python.exe scripts\list_portfolios.py
```
