import yfinance as yf
import pandas as pd

class MarketFetcher:
    def __init__(self, tickers: list):
        # Garante que todos os tickers tenham o .SA (padrão B3 no yfinance)
        self.tickers = [t if t.endswith('.SA') else f"{t}.SA" for t in tickers]

    def obter_dados_historicos(self, periodo="2y"):
        try:
            # Baixamos os dados
            dados = yf.download(self.tickers, period=periodo)
            
            # O yfinance pode retornar um MultiIndex. Vamos extrair o 'Adj Close' com segurança.
            if 'Adj Close' in dados.columns:
                precos = dados['Adj Close']
            elif 'Close' in dados.columns:
                precos = dados['Close']
            else:
                return None
                
            if precos.empty:
                return None
                
            return precos
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return None