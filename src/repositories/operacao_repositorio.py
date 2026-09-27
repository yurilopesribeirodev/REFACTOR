# src/repositories/operacao_repositorio.py
from datetime import date
from database.conexao import obter_conexao
from models.ativo import Ativo
from models.operacao import Operacao, TipoOperacao


class OperacaoRepositorio:
    def salvar(self, operacao: Operacao):
        conexao = obter_conexao()
        conexao.execute(
            """INSERT INTO operacoes (ticker, tipo, quantidade, preco, data)
               VALUES (?, ?, ?, ?, ?)""",
            (operacao.ativo.ticker, operacao.tipo.value,
             operacao.quantidade, operacao.preco, operacao.data.isoformat())
        )
        conexao.commit()
        conexao.close()

    def listar_todas(self, ordem_cronologica=True) -> list[Operacao]:
        conexao = obter_conexao()

        ordenacao = "ASC" if ordem_cronologica else "DESC"
        linhas = conexao.execute(f"""
            SELECT o.id, o.ticker, a.nome, o.tipo, o.quantidade, o.preco, o.data
            FROM operacoes o
            JOIN ativos a ON a.ticker = o.ticker
            ORDER BY o.data {ordenacao}, o.id {ordenacao}
        """).fetchall()
        conexao.close()

        operacoes = []
        for l in linhas:
            ativo = Ativo(l["ticker"], l["nome"])
            operacoes.append(Operacao(
                id=l["id"], ativo=ativo, tipo=TipoOperacao(l["tipo"]),
                quantidade=l["quantidade"], preco=l["preco"],
                data=date.fromisoformat(l["data"])
            ))
        return operacoes

    def excluir(self, id_operacao: int):
        conexao = obter_conexao()
        conexao.execute("DELETE FROM operacoes WHERE id = ?", (id_operacao,))
        conexao.commit()
        conexao.close()

        