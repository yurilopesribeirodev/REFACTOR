# src/models/posicao.py
from models.operacao import TipoOperacao


class Posicao:
    def __init__(self, ativo):
        self.ativo = ativo
        self.quantidade = 0
        self.preco_medio = 0.0

    def aplicar(self, operacao):
        if operacao.ativo.ticker != self.ativo.ticker:
            raise ValueError("Operação não pertence a este ativo")

        if operacao.tipo == TipoOperacao.COMPRA:
            total_atual = self.quantidade * self.preco_medio
            total_novo = operacao.quantidade * operacao.preco
            self.quantidade += operacao.quantidade
            self.preco_medio = (total_atual + total_novo) / self.quantidade
        else:  # VENDA
            if operacao.quantidade > self.quantidade:
                raise ValueError("Quantidade insuficiente para venda")
            self.quantidade -= operacao.quantidade

    def esta_zerada(self) -> bool:
        return self.quantidade == 0

    def valor_investido(self) -> float:
        return self.quantidade * self.preco_medio

    def lucro(self, preco_atual: float) -> float:
        return (preco_atual - self.preco_medio) * self.quantidade