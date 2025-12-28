import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresConnector:
    
    def __init__(self):
        # Conecta ao servidor PostgreSQL
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )

    def inicializar_banco(self, sql_file_path):
        """Lê o arquivo .sql e cria o schema/tabelas se não existirem."""
        try:
            if not os.path.exists(sql_file_path):
                print(f"❌ Arquivo SQL não encontrado em: {sql_file_path}")
                return

            with open(sql_file_path, 'r') as f:
                sql_script = f.read()
            
            with self.conn.cursor() as cur:
                cur.execute(sql_script)
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
                cur.execute("""
                    INSERT INTO quant_engine.portfolios (user_id, expected_return, volatility, sharpe_ratio)
                    VALUES (%s, %s, %s, %s) RETURNING id;
                """, (user_id, metrics['return'], metrics['risk'], metrics['sharpe'])) 
                
                p_id = cur.fetchone()[0]
                
                # 2. Insere cada ativo daquela carteira
                for ticker, w in weights.items():
                    # Remove o sufixo .SA se quiser salvar o ticker limpo, ou mantém
                    ticker_clean = ticker.replace(".SA", "")
                    cur.execute("""
                        INSERT INTO quant_engine.portfolio_assets (portfolio_id, ticker, weight)
                        VALUES (%s, %s, %s);
                    """, (p_id, ticker_clean, w))
                    
                self.conn.commit()
                print(f"✅ Carteira {p_id} salva no PostgreSQL!")
        except Exception as e:
            print(f"❌ Erro ao salvar resultado: {e}")
            self.conn.rollback()