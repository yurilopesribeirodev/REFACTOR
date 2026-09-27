# src/models/operacao.py
from datetime import date
from enum import Enum


class TipoOperacao(Enum):
    COMPRA = "compra"
    VENDA = "venda"


class Operacao:
    def __init__(self, ativo, tipo: TipoOperacao, quantidade: int, preco: float,
                 data: date, id: int = None):
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser positiva")
        if preco <= 0:
            raise ValueError("Preço deve ser positivo")

        self.id = id
        self.ativo = ativo
        self.tipo = tipo
        self.quantidade = quantidade
        self.preco = preco
        self.data = data

    @property
    def valor_total(self) -> float:
        return self.quantidade * self.preco