import streamlit as st
import pandas as pd
import plotly.express as px
from core import optimizer
from data.market_fetcher import MarketFetcher

st.set_page_config(page_title="QuantMind Engine", layout="wide")

st.title("🧠 QuantMind: Inteligência Financeira")

# Sidebar
st.sidebar.header("Configurações")
tickers_input = st.sidebar.text_input("Ativos (separados por vírgula)", "PETR4, VALE3, ITUB4, ABEV3")
n_sim = st.sidebar.slider("Simulações de Monte Carlo", 1000, 10000, 5000)

if st.sidebar.button("Otimizar Carteira"):
    tickers = [t.strip() for t in tickers_input.split(',')]
               
    with st.spinner('Processando...'):
        # Coleta de dados
        fetcher = MarketFetcher(tickers)
        dados = fetcher.obter_dados_historicos()
        
        if dados is not None:
            # Lógica Matemática
            retornos = dados.pct_change().dropna()
            opt = optimizer(retornos)
            df_sim = opt.run_monte_carlo(n_simulations=n_sim)
            
            # Gráfico de Dispersão (Fronteira Eficiente)
            fig = px.scatter(df_sim, x="Risk", y="Return", color="Sharpe",
                             title="Fronteira Eficiente - Risco vs Retorno",
                             labels={'Risk': 'Risco (Volatilidade)', 'Return': 'Retorno Esperado'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Exibe a melhor carteira
            melhor_sharpe = df_sim.iloc[df_sim['Sharpe'].idxmax()]
            st.success("Melhor carteira encontrada!")
            st.write(melhor_sharpe)
        else:
            st.error("Erro ao buscar dados. Verifique os tickers.")