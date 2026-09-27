# src/views/tela_cadastro_operacao.py
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from models.ativo import Ativo
from models.operacao import Operacao, TipoOperacao
from repositories.ativo_repositorio import AtivoRepositorio
from repositories.operacao_repositorio import OperacaoRepositorio
from services.cotacao_service import CotacaoService
from views.estilo import (
    COR_FUNDO, COR_CARD, COR_ACCENT, COR_ACCENT_HOVER, COR_TEXTO,
    COR_TEXTO_SECUNDARIO, COR_BORDA, FONTE_TITULO, FONTE_LABEL,
    FONTE_BOTAO, FONTE_INPUT, PADDING_JANELA
)


class TelaCadastroOperacao(ctk.CTkToplevel):
    def __init__(self, master, ao_salvar, carteira):
        super().__init__(master)
        self.title("Nova operação")
        self.geometry("420x560")
        self.resizable(False, False)
        self.configure(fg_color=COR_FUNDO)
        self.ao_salvar = ao_salvar
        self.carteira = carteira          # <- guarda a referência

        self.ativo_repo = AtivoRepositorio()
        self.operacao_repo = OperacaoRepositorio()
        self.cotacao_service = CotacaoService()

        self._montar_widgets()

    def _montar_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="n", padx=PADDING_JANELA, pady=PADDING_JANELA)

        ctk.CTkLabel(container, text="Nova operação", font=FONTE_TITULO,
                     text_color=COR_TEXTO).pack(anchor="center", pady=(0, 24))

        campo_ticker = self._criar_campo(container, "Ticker")
        self.entrada_ticker = ctk.CTkEntry(campo_ticker, placeholder_text="ex: PETR4",
                                            font=FONTE_INPUT, height=44,
                                            fg_color=COR_CARD, border_color=COR_BORDA,
                                            text_color=COR_TEXTO, justify="center")
        self.entrada_ticker.pack(fill="x")

        ctk.CTkLabel(container, text="Tipo de operação", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(16, 8))
        self.tipo_var = ctk.StringVar(value="compra")
        frame_tipo = ctk.CTkFrame(container, fg_color="transparent")
        frame_tipo.pack(fill="x")
        frame_tipo.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkRadioButton(frame_tipo, text="Compra", variable=self.tipo_var, value="compra",
                           fg_color=COR_ACCENT, font=FONTE_LABEL,
                           text_color=COR_TEXTO).grid(row=0, column=0, sticky="w")
        ctk.CTkRadioButton(frame_tipo, text="Venda", variable=self.tipo_var, value="venda",
                           fg_color=COR_ACCENT, font=FONTE_LABEL,
                           text_color=COR_TEXTO).grid(row=0, column=1, sticky="w")

        campo_qtd = self._criar_campo(container, "Quantidade")
        self.entrada_quantidade = ctk.CTkEntry(campo_qtd, placeholder_text="ex: 100",
                                                font=FONTE_INPUT, height=44,
                                                fg_color=COR_CARD, border_color=COR_BORDA,
                                                text_color=COR_TEXTO, justify="center")
        self.entrada_quantidade.pack(fill="x")

        campo_preco = self._criar_campo(container, "Preço")
        self.entrada_preco = ctk.CTkEntry(campo_preco, placeholder_text="ex: 35.50",
                                           font=FONTE_INPUT, height=44,
                                           fg_color=COR_CARD, border_color=COR_BORDA,
                                           text_color=COR_TEXTO, justify="center")
        self.entrada_preco.pack(fill="x")

        self.botao_cadastrar = ctk.CTkButton(
            container, text="Cadastrar", fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER,
            font=FONTE_BOTAO, height=46, command=self._cadastrar
        )
        self.botao_cadastrar.pack(fill="x", pady=(24, 0))

    def _criar_campo(self, container, rotulo):
        bloco = ctk.CTkFrame(container, fg_color="transparent")
        bloco.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(bloco, text=rotulo, font=FONTE_LABEL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(0, 8))
        return bloco

    def _cadastrar(self):
        ticker = self.entrada_ticker.get().upper().strip()

        if not ticker:
            messagebox.showerror("Erro", "Digite um ticker")
            return

        try:
            quantidade = int(self.entrada_quantidade.get())
            preco = float(self.entrada_preco.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos")
            return

        tipo = TipoOperacao(self.tipo_var.get())

        # VALIDA SALDO ANTES DE QUALQUER CHAMADA À API OU AO BANCO
        if tipo == TipoOperacao.VENDA:
            posicao_atual = self.carteira.posicoes.get(ticker)
            quantidade_disponivel = posicao_atual.quantidade if posicao_atual else 0

            if quantidade > quantidade_disponivel:
                messagebox.showerror(
                    "Erro",
                    f"Você tem {quantidade_disponivel} unidades de {ticker}, "
                    f"não é possível vender {quantidade}"
                )
                return

        self.botao_cadastrar.configure(state="disabled", text="Verificando...")
        self.update()

        info = self.cotacao_service.buscar_cotacao(ticker)

        if info is None:
            messagebox.showerror("Erro", f"Ticker '{ticker}' não encontrado")
            self.botao_cadastrar.configure(state="normal", text="Cadastrar")
            return

        try:
            ativo = Ativo(ticker, info["nome"])
            self.ativo_repo.salvar(ativo)

            operacao = Operacao(
                ativo=ativo, tipo=tipo, quantidade=quantidade,
                preco=preco, data=date.today()
            )
            self.operacao_repo.salvar(operacao)

            self.ao_salvar()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            self.botao_cadastrar.configure(state="normal", text="Cadastrar")