# src/models/ativo.py
class Ativo:
    def __init__(self, ticker: str, nome: str):
        self.ticker = ticker
        self.nome = nome

    def __repr__(self):
        return f"Ativo({self.ticker})"