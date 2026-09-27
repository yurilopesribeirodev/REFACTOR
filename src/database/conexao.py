# src/database/conexao.py
import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent.parent.parent / "carteira.db"


def obter_conexao() -> sqlite3.Connection:
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    conexao = obter_conexao()
    conexao.executescript("""
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS operacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (ticker) REFERENCES ativos(ticker)
        );
    """)
    conexao.commit()
    conexao.close()