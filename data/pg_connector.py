import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresConnector:
    
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", 5432)
        )
        
    def salvar_resultado(self, user_id, metrics, weights):
        with self.conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO quant_engine.portfolios (user_id, expected_return, volatility, sharpe_ratio)
                        VALUES (%s, %s, %s, %s) RETURNING id;
                        """, (user_id, metrics['return'], metrics['risk'], metrics['sharpe'])) 
            
            p_id = cur.fetchone()[0]
            
            for ticker, w in weights.items():
                cur.execute("""
                            INSERT INTO quant_engine.portfolio_assets (portfolio_id, ticker, weight)
                            VALUES (%s, %s, %s);
                            """, (p_id, ticker, w))
                
            self.conn.commit()
                