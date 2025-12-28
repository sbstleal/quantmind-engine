import psycopg2
import pg8000
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresConnector:
    
    def __init__(self):
        # Conecta ao servidor PostgreSQL
        host = os.getenv("DB_HOST")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        port = os.getenv("DB_PORT", "5432")

        # Usa uma DSN explícita — às vezes evita problemas de decoding
        dsn = f"host={host} dbname={dbname} user={user} password={password} port={port}"
        try:
            self.conn = psycopg2.connect(dsn)
        except UnicodeDecodeError:
            # Se psycopg2/libpq falhar devido a problemas de encoding no ambiente,
            # tenta usar o driver puro-Python `pg8000` como fallback.
            print("⚠️ psycopg2 falhou por UnicodeDecodeError — tentando fallback com pg8000 (puro-Python)")
            try:
                self.conn = pg8000.connect(host=host, database=dbname, user=user, password=password, port=int(port))
            except Exception as e:
                # Se o erro for de database inexistente, tenta criar o banco conectando-se ao DB padrão 'postgres'
                err_str = str(e)
                if '3D000' in err_str or 'does not exist' in err_str or 'n\u00e3o existe' in err_str:
                    try:
                        print(f"⚠️ Banco '{dbname}' não existe — tentando criar automaticamente...")
                        admin_conn = pg8000.connect(host=host, database='postgres', user=user, password=password, port=int(port))
                        # CREATE DATABASE não pode ser executado dentro de transação, habilita autocommit
                        try:
                            admin_conn.autocommit = True
                        except Exception:
                            pass
                        with admin_conn.cursor() as acur:
                            acur.execute(f'CREATE DATABASE "{dbname}"')
                        admin_conn.close()
                        # Agora reconecta ao DB recém-criado
                        self.conn = pg8000.connect(host=host, database=dbname, user=user, password=password, port=int(port))
                    except Exception as e2:
                        safe_pass = None if password is None else "***"
                        print(f"❌ Não foi possível criar o banco '{dbname}' automaticamente: {e2} — host={host} user={user} pwd={safe_pass}")
                        raise
                else:
                    safe_pass = None if password is None else "***"
                    print(f"❌ Falha ao conectar ao PostgreSQL com pg8000 — host={host} db={dbname} user={user} port={port} pwd={safe_pass}")
                    raise
        except Exception:
            safe_pass = None if password is None else "***"
            print(f"❌ Falha ao conectar ao PostgreSQL — host={host} db={dbname} user={user} port={port} pwd={safe_pass}")
            raise

    def inicializar_banco(self, sql_file_path):
        """Lê o arquivo .sql e cria o schema/tabelas se não existirem."""
        try:
            if not os.path.exists(sql_file_path):
                print(f"❌ Arquivo SQL não encontrado em: {sql_file_path}")
                return

            # Tenta ler como UTF-8 e, se falhar, faz fallback para Latin-1
            try:
                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
            except UnicodeDecodeError:
                with open(sql_file_path, 'r', encoding='latin-1') as f:
                    sql_script = f.read()

            # Executa cada statement SQL separadamente para maior compatibilidade
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            with self.conn.cursor() as cur:
                for stmt in statements:
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        # Não interrompe a inicialização por causa de uma statement problemática
                        print(f"⚠️ Ignorando statement com erro: {e}")
                self.conn.commit()
                print("✅ Estrutura do Banco de Dados pronta (Schema e Tabelas).")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            self.conn.rollback()
        
    def salvar_resultado(self, user_id, metrics, weights):
        """Salva a carteira e seus ativos vinculados."""
        try:
            with self.conn.cursor() as cur:
                # 1. Insere o resumo da carteira
                # Normaliza tipos (especialmente np.float64) para floats nativos
                ret = float(metrics['return'])
                risk = float(metrics['risk'])
                sharpe = float(metrics['sharpe'])

                cur.execute("""
                    INSERT INTO quant_engine.portfolios (user_id, expected_return, volatility, sharpe_ratio)
                    VALUES (%s, %s, %s, %s) RETURNING id;
                """, (user_id, ret, risk, sharpe)) 
                
                p_id = cur.fetchone()[0]
                
                # 2. Insere cada ativo daquela carteira
                for ticker, w in weights.items():
                    # Remove o sufixo .SA se quiser salvar o ticker limpo, ou mantém
                    ticker_clean = ticker.replace(".SA", "")
                    cur.execute("""
                        INSERT INTO quant_engine.portfolio_assets (portfolio_id, ticker, weight)
                        VALUES (%s, %s, %s);
                    """, (p_id, ticker_clean, float(w)))
                    
                self.conn.commit()
                print(f"✅ Carteira {p_id} salva no PostgreSQL!")
        except Exception as e:
            print(f"❌ Erro ao salvar resultado: {e}")
            self.conn.rollback()