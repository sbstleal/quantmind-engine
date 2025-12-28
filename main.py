import os
from dotenv import load_dotenv
from data.market_fetcher import MarketFetcher
from core.optimizer import PortfolioOptimizer
from data.pg_connector import PostgresConnector

def run_pipeline():
    load_dotenv()
    print("--- 🧠 Iniciando QuantMind Engine ---")
    
    # 1. Inicializa o Banco e as Tabelas
    try:
        db = PostgresConnector()
        # Aqui ele lê o seu setup_db.sql e cria tudo sozinho!
        db.inicializar_banco('database/setup_db.sql')
        
        # 2. Garante que existe um usuário para o teste
        with db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO quant_engine.users (id, name, risk_profile) 
                VALUES (1, 'Admin QuantMind', 'Agressivo')
                ON CONFLICT (id) DO NOTHING;
            """)
            db.conn.commit()
    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        return

    # 3. Coleta de Dados (B3)
    tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'ABEV3.SA']
    fetcher = MarketFetcher(tickers)
    dados = fetcher.obter_dados_historicos()
    
    if dados is not None:
        # 4. Otimização Matemática
        retornos = dados.pct_change().dropna()
        optimizer = PortfolioOptimizer(retornos)
        resultados = optimizer.run_monte_carlo(n_simulations=1000)
        
        melhor_carteira = resultados.iloc[resultados['Sharpe'].idxmax()]
        
        # 5. Persistência
        pesos = melhor_carteira.filter(like='W_').to_dict()
        metrics = {
            'return': melhor_carteira['Return'],
            'risk': melhor_carteira['Risk'],
            'sharpe': melhor_carteira['Sharpe']
        }
        
        db.salvar_resultado(user_id=1, metrics=metrics, weights=pesos)
        print("\n✅ Processo finalizado com sucesso!")
    else:
        print("❌ Erro ao obter dados do Yahoo Finance.")

if __name__ == "__main__":
    run_pipeline()