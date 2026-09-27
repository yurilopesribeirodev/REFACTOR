# src/models/carteira.py
from models.posicao import Posicao


class Carteira:
    def __init__(self):
        self.posicoes: dict[str, Posicao] = {}

    def registrar(self, operacao):
        ticker = operacao.ativo.ticker

        if ticker not in self.posicoes:
            self.posicoes[ticker] = Posicao(operacao.ativo)

        self.posicoes[ticker].aplicar(operacao)

        if self.posicoes[ticker].esta_zerada():
            del self.posicoes[ticker]

    def valor_total_investido(self) -> float:
        return sum(p.valor_investido() for p in self.posicoes.values())

    def listar_posicoes(self) -> list[Posicao]:
        return list(self.posicoes.values())