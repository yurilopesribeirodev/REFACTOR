# src/repositories/ativo_repositorio.py
from database.conexao import obter_conexao
from models.ativo import Ativo


class AtivoRepositorio:
    def salvar(self, ativo: Ativo):
        conexao = obter_conexao()
        conexao.execute(
            "INSERT OR IGNORE INTO ativos (ticker, nome) VALUES (?, ?)",
            (ativo.ticker, ativo.nome)
        )
        conexao.commit()
        conexao.close()

    def buscar_por_ticker(self, ticker: str) -> Ativo | None:
        conexao = obter_conexao()
        linha = conexao.execute(
            "SELECT * FROM ativos WHERE ticker = ?", (ticker,)
        ).fetchone()
        conexao.close()

        if linha is None:
            return None
        return Ativo(linha["ticker"], linha["nome"])

    def listar_todos(self) -> list[Ativo]:
        conexao = obter_conexao()
        linhas = conexao.execute("SELECT * FROM ativos").fetchall()
        conexao.close()
        return [Ativo(l["ticker"], l["nome"]) for l in linhas]