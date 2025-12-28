CREATE SCHEMA IF NOT EXISTS quant_engine;

CREATE TABLE IF NOT EXISTS quant_engine.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    risk_profile VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS quant_engine.portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES quant_engine.users(id),
    expected_return DECIMAL(10, 4),
    volatility DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quant_engine.portfolio_assets (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES quant_engine.portfolios(id),
    ticker VARCHAR(10) NOT NULL,
    weight DECIMAL(5, 4) NOT NULL
);