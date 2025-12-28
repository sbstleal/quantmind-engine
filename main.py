import os
from dotenv import load_dotenv
from data.market_fetcher import MarketFetcher
from core.optimizer import PortfolioOptimizer
from data.pg_connector import PostgresConnector

def run_pipeline():
    # 1. Carrega as variáveis do .env (Banco de Dados)
    load_dotenv()
    
    print("--- 🧠 Iniciando QuantMind Engine ---")
    
    # 2. Definição dos ativos para teste
    tickers = ['PETR4', 'VALE3', 'ITUB4', 'ABEV3']
    
    # 3. Coleta de Dados
    print(f"Buscando dados para: {tickers}...")
    fetcher = MarketFetcher(tickers)
    dados = fetcher.obter_dados_historicos()
    
    if dados is None:
        print("❌ Falha ao buscar dados da B3.")
        return

    # 4. Processamento Matemático (Álgebra Linear / Estatística)
    print("Calculando retornos e otimizando carteira...")
    retornos = dados.pct_change().dropna()
    optimizer = PortfolioOptimizer(retornos)
    
    # Rodamos uma simulação menor (1000) apenas para teste
    resultados = optimizer.run_monte_carlo(n_simulations=1000)
    
    # Pegamos a melhor carteira (Maior Sharpe Ratio)
    melhor_carteira = resultados.iloc[resultados['Sharpe'].idxmax()]
    
    print("\n✅ Otimização Concluída!")
    print(f"Retorno Esperado: {melhor_carteira['Return']:.2%}")
    print(f"Risco (Volatilidade): {melhor_carteira['Risk']:.2%}")
    print("-" * 30)

    # 5. Persistência no PostgreSQL
    print("Tentando salvar no Banco de Dados...")
    try:
        # Extrai os pesos (colunas que começam com W_)
        pesos = melhor_carteira.filter(like='W_').to_dict()
        metrics = {
            'return': melhor_carteira['Return'],
            'risk': melhor_carteira['Risk'],
            'sharpe': melhor_carteira['Sharpe']
        }
        
        db = PostgresConnector()
        # Aqui assumimos que você tem um usuário com ID 1 no banco para teste
        db.salvar_resultado(user_id=1, metrics=metrics, weights=pesos)
        print("✅ Dados salvos no PostgreSQL com sucesso!")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar no banco: {e}")
        print("Dica: Verifique se o banco 'quantmind_db' existe e o .env está correto.")

if __name__ == "__main__":
    run_pipeline()