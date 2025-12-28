import yfinance as yf   
import pandas as pd

class MarketFetcher:
    
    def __init__(self, tickers: list):
        self.tickers = [t if t.endswith('.SA') else f"{t}.SA" for t in tickers]
        
    def obter_dados_historicos(self, periodo="2y"):
        try:
            dados = yf.download(self.tickers, period=periodo)['Adj Close']
            if dados.empty:
                return None
            return dados
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return None
        
        