import os
import sys
import pathlib
from dotenv import load_dotenv

# Ajusta sys.path para permitir imports relativos quando executado como script
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.pg_connector import PostgresConnector


def listar_carteiras():
    load_dotenv()
    db = PostgresConnector()

    with db.conn.cursor() as cur:
        cur.execute("SELECT id, user_id, expected_return, volatility, sharpe_ratio, created_at FROM quant_engine.portfolios ORDER BY id;")
        portfolios = cur.fetchall()

        if not portfolios:
            print('Nenhuma carteira encontrada.')
            return

        for p in portfolios:
            p_id, user_id, expected_return, volatility, sharpe_ratio, created_at = p
            print('---')
            print(f'Carteira ID: {p_id} | Usuário: {user_id} | Retorno: {expected_return} | Volatilidade: {volatility} | Sharpe: {sharpe_ratio} | Criada: {created_at}')
            # Buscar ativos
            cur.execute("SELECT ticker, weight FROM quant_engine.portfolio_assets WHERE portfolio_id = %s ORDER BY id;", (p_id,))
            ativos = cur.fetchall()
            if ativos:
                print(' Ativos:')
                for a in ativos:
                    ticker, weight = a
                    print(f'  - {ticker}: {weight}')
            else:
                print('  (sem ativos vinculados)')


if __name__ == '__main__':
    listar_carteiras()
