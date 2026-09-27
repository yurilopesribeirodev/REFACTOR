import customtkinter as ctk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models.carteira import Carteira
from models.operacao import TipoOperacao
from repositories.operacao_repositorio import OperacaoRepositorio
from services.cotacao_service import CotacaoService
from views.tela_cadastro_operacao import TelaCadastroOperacao
from views.estilo import (
    configurar_tema, COR_FUNDO, COR_CARD, COR_CARD_CLARO, COR_ACCENT, COR_ACCENT_HOVER,
    COR_TEXTO, COR_TEXTO_SECUNDARIO, COR_BORDA, COR_LUCRO, COR_PREJUIZO,
    COR_COMPRA, COR_VENDA, COR_LINHA_PAR, COR_LINHA_IMPAR, COR_LINHA_SELECIONADA,
    CORES_GRAFICO, FONTE_TITULO, FONTE_SUBTITULO, FONTE_TOTAL, FONTE_LABEL,
    FONTE_TABELA, FONTE_TABELA_CABECALHO, FONTE_BOTAO, PADDING_CARD, PADDING_JANELA
)

configurar_tema()


class TelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Carteira de Ativos")
        self.geometry("1140x680")
        self.minsize(940, 560)
        self.configure(fg_color=COR_FUNDO)

        self.operacao_repo = OperacaoRepositorio()
        self.cotacao_service = CotacaoService()
        self.carteira = Carteira()
        self.visao_grafico_atual = "distribuicao"
        self.precos_atuais = {}

        self._montar_estilo_treeview()
        self._montar_widgets()
        self._carregar_tudo()

    # ---------- ESTILO DA TABELA (ttk puro, fora do customtkinter) ----------

    def _montar_estilo_treeview(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Custom.Treeview", rowheight=42, font=FONTE_TABELA,
                          background=COR_CARD, fieldbackground=COR_CARD,
                          foreground=COR_TEXTO, borderwidth=0)
        estilo.configure("Custom.Treeview.Heading", font=FONTE_TABELA_CABECALHO,
                          background=COR_CARD_CLARO, foreground=COR_TEXTO_SECUNDARIO,
                          relief="flat", padding=(12, 12))
        estilo.map("Custom.Treeview",
                   background=[("selected", COR_LINHA_SELECIONADA)],
                   foreground=[("selected", COR_TEXTO)])

    # ---------- MONTAGEM GERAL ----------

    def _montar_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # barra superior
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=PADDING_JANELA, pady=(PADDING_JANELA, 14))
        barra.grid_columnconfigure(0, weight=1)

        bloco_titulo = ctk.CTkFrame(barra, fg_color="transparent")
        bloco_titulo.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(bloco_titulo, text="Minha carteira", font=FONTE_TITULO,
                     text_color=COR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(bloco_titulo, text="Acompanhe suas posições e lançamentos",
                     font=FONTE_LABEL, text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", pady=(4, 0))

        botoes = ctk.CTkFrame(barra, fg_color="transparent")
        botoes.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(botoes, text="Atualizar", fg_color=COR_CARD, text_color=COR_TEXTO,
                      hover_color=COR_CARD_CLARO, border_width=1, border_color=COR_BORDA,
                      font=FONTE_BOTAO, height=40, width=120,
                      command=self._carregar_tudo).pack(side="left", padx=6)
        ctk.CTkButton(botoes, text="+  Nova operação", fg_color=COR_ACCENT,
                      hover_color=COR_ACCENT_HOVER, font=FONTE_BOTAO, height=40, width=170,
                      command=self._abrir_cadastro).pack(side="left", padx=6)

        # abas
        self.abas = ctk.CTkTabview(
            self, fg_color="transparent",
            segmented_button_fg_color=COR_CARD,
            segmented_button_selected_color=COR_ACCENT,
            segmented_button_selected_hover_color=COR_ACCENT_HOVER,
            segmented_button_unselected_color=COR_CARD,
            text_color=COR_TEXTO,
        )
        self.abas.grid(row=1, column=0, sticky="nsew", padx=PADDING_JANELA, pady=(0, PADDING_JANELA))
        self.abas.add("Carteira")
        self.abas.add("Lançamentos")
        self.abas._segmented_button.configure(font=FONTE_BOTAO, height=38)

        self._montar_aba_carteira(self.abas.tab("Carteira"))
        self._montar_aba_lancamentos(self.abas.tab("Lançamentos"))

    # ---------- ABA CARTEIRA (tabela de posições + gráfico) ----------

    def _montar_aba_carteira(self, aba):
        aba.grid_columnconfigure(0, weight=2)
        aba.grid_columnconfigure(1, weight=1)
        aba.grid_rowconfigure(0, weight=1)

        # card da tabela de posições
        card = ctk.CTkFrame(aba, fg_color=COR_CARD, corner_radius=16)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(card, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=PADDING_CARD, pady=(PADDING_CARD, 8))
        ctk.CTkLabel(cabecalho, text="Total investido", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        self.label_total = ctk.CTkLabel(cabecalho, text="R$ 0,00", font=FONTE_TOTAL,
                                         text_color=COR_TEXTO)
        self.label_total.pack(anchor="w", pady=(2, 0))

        colunas = ("ticker", "quantidade", "preco_medio", "preco_atual", "lucro")
        self.tabela_carteira = ttk.Treeview(card, columns=colunas, show="headings",
                                             style="Custom.Treeview")
        for col, titulo in zip(colunas, ["Ticker", "Qtd", "Preço médio", "Preço atual", "Lucro"]):
            self.tabela_carteira.heading(col, text=titulo, anchor="center")
            self.tabela_carteira.column(col, anchor="center")
        self.tabela_carteira.grid(row=1, column=0, sticky="nsew",
                                   padx=PADDING_CARD, pady=(0, PADDING_CARD))

        # card do gráfico (distribuição / rentabilidade)
        card_grafico = ctk.CTkFrame(aba, fg_color=COR_CARD, corner_radius=16)
        card_grafico.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        card_grafico.grid_columnconfigure(0, weight=1)
        card_grafico.grid_rowconfigure(1, weight=1)

        cabecalho_grafico = ctk.CTkFrame(card_grafico, fg_color="transparent")
        cabecalho_grafico.grid(row=0, column=0, sticky="ew", padx=PADDING_CARD, pady=(PADDING_CARD, 8))

        self.botao_distribuicao = ctk.CTkButton(
            cabecalho_grafico, text="Distribuição", font=FONTE_BOTAO, height=32,
            fg_color=COR_ACCENT, hover_color=COR_ACCENT_HOVER,
            command=lambda: self._trocar_visao_grafico("distribuicao")
        )
        self.botao_distribuicao.pack(side="left", padx=(0, 8))

        self.botao_rentabilidade = ctk.CTkButton(
            cabecalho_grafico, text="Rentabilidade", font=FONTE_BOTAO, height=32,
            fg_color=COR_CARD_CLARO, text_color=COR_TEXTO_SECUNDARIO,
            hover_color=COR_CARD_CLARO,
            command=lambda: self._trocar_visao_grafico("rentabilidade")
        )
        self.botao_rentabilidade.pack(side="left")

        self.frame_grafico = ctk.CTkFrame(card_grafico, fg_color=COR_CARD)
        self.frame_grafico.grid(row=1, column=0, sticky="nsew",
                                 padx=PADDING_CARD, pady=(0, PADDING_CARD))

    # ---------- ABA LANÇAMENTOS (histórico de operações) ----------

    def _montar_aba_lancamentos(self, aba):
        aba.grid_columnconfigure(0, weight=1)
        aba.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(aba, fg_color=COR_CARD, corner_radius=16)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        cabecalho = ctk.CTkFrame(card, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=PADDING_CARD, pady=(PADDING_CARD, 8))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cabecalho, text="Histórico de lançamentos", font=FONTE_SUBTITULO,
                     text_color=COR_TEXTO).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(cabecalho, text="Excluir selecionado", fg_color=COR_CARD_CLARO,
                      text_color=COR_PREJUIZO, border_width=1, border_color=COR_BORDA,
                      hover_color="#2A1D22", font=FONTE_BOTAO, height=36, width=180,
                      command=self._excluir_lancamento).grid(row=0, column=1, sticky="e")

        colunas = ("ticker", "tipo", "quantidade", "preco", "total", "data")
        self.tabela_lancamentos = ttk.Treeview(card, columns=colunas, show="headings",
                                                style="Custom.Treeview")
        titulos = ["Ativo", "Tipo", "Quantidade", "Preço unitário", "Total", "Data"]
        for col, titulo in zip(colunas, titulos):
            self.tabela_lancamentos.heading(col, text=titulo, anchor="center")
            self.tabela_lancamentos.column(col, anchor="center")
        self.tabela_lancamentos.grid(row=1, column=0, sticky="nsew",
                                      padx=PADDING_CARD, pady=(0, PADDING_CARD))

    def _excluir_lancamento(self):
        selecionado = self.tabela_lancamentos.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione um lançamento para excluir")
            return

        item = self.tabela_lancamentos.item(selecionado[0])
        id_operacao = item["tags"][-1]

        if messagebox.askyesno("Confirmar", "Excluir este lançamento?"):
            self.operacao_repo.excluir(int(id_operacao))
            self._carregar_tudo()

    # ---------- CARREGAMENTO / ATUALIZAÇÃO DE DADOS ----------

    def _carregar_tudo(self):
        operacoes = self.operacao_repo.listar_todas()

        self.carteira = Carteira()
        for operacao in operacoes:
            self.carteira.registrar(operacao)

        # busca cada cotação UMA VEZ e guarda em cache, evitando
        # chamadas repetidas à API ao trocar de aba/gráfico
        self.precos_atuais = {}
        for posicao in self.carteira.listar_posicoes():
            info = self.cotacao_service.buscar_cotacao(posicao.ativo.ticker)
            self.precos_atuais[posicao.ativo.ticker] = (
                info["preco_atual"] if info else posicao.preco_medio
            )

        self._atualizar_tabela_carteira()
        self._atualizar_tabela_lancamentos(operacoes)
        self._atualizar_grafico()

    def _atualizar_tabela_carteira(self):
        for item in self.tabela_carteira.get_children():
            self.tabela_carteira.delete(item)

        for i, posicao in enumerate(self.carteira.listar_posicoes()):
            preco_atual = self.precos_atuais[posicao.ativo.ticker]
            lucro = posicao.lucro(preco_atual)

            tag_lucro = "lucro" if lucro >= 0 else "prejuizo"
            self.tabela_carteira.insert("", "end", values=(
                posicao.ativo.ticker, posicao.quantidade,
                f"R$ {posicao.preco_medio:.2f}", f"R$ {preco_atual:.2f}",
                f"R$ {lucro:.2f}"
            ), tags=(tag_lucro, f"linha{i % 2}"))

        self.tabela_carteira.tag_configure("lucro", foreground=COR_LUCRO)
        self.tabela_carteira.tag_configure("prejuizo", foreground=COR_PREJUIZO)
        self.tabela_carteira.tag_configure("linha0", background=COR_LINHA_PAR)
        self.tabela_carteira.tag_configure("linha1", background=COR_LINHA_IMPAR)

        self.label_total.configure(
            text=f"R$ {self.carteira.valor_total_investido():.2f}"
        )

    def _atualizar_tabela_lancamentos(self, operacoes):
        for item in self.tabela_lancamentos.get_children():
            self.tabela_lancamentos.delete(item)

        for i, op in enumerate(operacoes):
            tag_cor = "compra" if op.tipo == TipoOperacao.COMPRA else "venda"
            self.tabela_lancamentos.insert("", "end", values=(
                op.ativo.ticker, op.tipo.value.capitalize(), op.quantidade,
                f"R$ {op.preco:.2f}", f"R$ {op.valor_total:.2f}",
                op.data.strftime("%d/%m/%Y")
            ), tags=(tag_cor, f"linha{i % 2}", str(op.id)))

        self.tabela_lancamentos.tag_configure("compra", foreground=COR_COMPRA)
        self.tabela_lancamentos.tag_configure("venda", foreground=COR_VENDA)
        self.tabela_lancamentos.tag_configure("linha0", background=COR_LINHA_PAR)
        self.tabela_lancamentos.tag_configure("linha1", background=COR_LINHA_IMPAR)

    # ---------- GRÁFICOS (dentro do próprio card, sem tela separada) ----------

    def _trocar_visao_grafico(self, visao):
        self.visao_grafico_atual = visao

        if visao == "distribuicao":
            self.botao_distribuicao.configure(fg_color=COR_ACCENT, text_color=COR_TEXTO)
            self.botao_rentabilidade.configure(fg_color=COR_CARD_CLARO, text_color=COR_TEXTO_SECUNDARIO)
        else:
            self.botao_rentabilidade.configure(fg_color=COR_ACCENT, text_color=COR_TEXTO)
            self.botao_distribuicao.configure(fg_color=COR_CARD_CLARO, text_color=COR_TEXTO_SECUNDARIO)

        self._atualizar_grafico()

    def _atualizar_grafico(self):
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()

        posicoes = self.carteira.listar_posicoes()
        if not posicoes:
            ctk.CTkLabel(self.frame_grafico, text="Sem posições ainda",
                         text_color=COR_TEXTO_SECUNDARIO, font=FONTE_LABEL).pack(pady=30)
            return

        if self.visao_grafico_atual == "distribuicao":
            self._desenhar_distribuicao(posicoes)
        else:
            self._desenhar_rentabilidade(posicoes)

    def _desenhar_distribuicao(self, posicoes):
        tickers = [p.ativo.ticker for p in posicoes]
        valores = [p.valor_investido() for p in posicoes]

        fig = Figure(figsize=(3.6, 3.6), dpi=100)
        fig.patch.set_facecolor(COR_CARD)
        eixo = fig.add_subplot(111)
        eixo.set_facecolor(COR_CARD)

        fatias, textos, autotextos = eixo.pie(
            valores, labels=tickers, autopct="%1.0f%%",
            colors=CORES_GRAFICO[:len(posicoes)],
            textprops={"fontsize": 11, "color": COR_TEXTO, "fontweight": "bold"},
            wedgeprops={"edgecolor": COR_CARD, "linewidth": 2}
        )
        for autotexto in autotextos:
            autotexto.set_color(COR_FUNDO)
            autotexto.set_fontweight("bold")

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        anotacao = eixo.annotate(
            "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc=COR_CARD_CLARO, ec=COR_ACCENT),
            color=COR_TEXTO, fontsize=10, fontweight="bold"
        )
        anotacao.set_visible(False)

        def ao_mover_mouse(evento):
            if evento.inaxes != eixo:
                if anotacao.get_visible():
                    anotacao.set_visible(False)
                    canvas.draw_idle()
                return
            for i, fatia in enumerate(fatias):
                contem, _ = fatia.contains(evento)
                if contem:
                    percentual = 100 * valores[i] / sum(valores)
                    anotacao.xy = (evento.xdata, evento.ydata)
                    anotacao.set_text(f"{tickers[i]}\nR$ {valores[i]:.2f} ({percentual:.0f}%)")
                    anotacao.set_visible(True)
                    canvas.draw_idle()
                    return
            if anotacao.get_visible():
                anotacao.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", ao_mover_mouse)

    def _desenhar_rentabilidade(self, posicoes):
        tickers = []
        lucros = []
        percentuais = []

        for p in posicoes:
            preco_atual = self.precos_atuais[p.ativo.ticker]
            lucro = p.lucro(preco_atual)
            percentual = (lucro / p.valor_investido() * 100) if p.valor_investido() > 0 else 0

            tickers.append(p.ativo.ticker)
            lucros.append(lucro)
            percentuais.append(percentual)

        lucro_total = sum(lucros)
        valor_total = sum(p.valor_investido() for p in posicoes)
        percentual_total = (lucro_total / valor_total * 100) if valor_total > 0 else 0

        indicadores = ctk.CTkFrame(self.frame_grafico, fg_color="transparent")
        indicadores.pack(fill="x", pady=(0, 12))

        cor_total = COR_LUCRO if lucro_total >= 0 else COR_PREJUIZO
        ctk.CTkLabel(indicadores, text="Resultado total", font=FONTE_LABEL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w")
        ctk.CTkLabel(indicadores, text=f"R$ {lucro_total:.2f}  ({percentual_total:+.1f}%)",
                     font=("Segoe UI", 18, "bold"), text_color=cor_total).pack(anchor="w")

        fig = Figure(figsize=(3.6, 2.6), dpi=100)
        fig.patch.set_facecolor(COR_CARD)
        eixo = fig.add_subplot(111)
        eixo.set_facecolor(COR_CARD)

        cores_barras = [COR_LUCRO if l >= 0 else COR_PREJUIZO for l in lucros]
        barras = eixo.bar(tickers, lucros, color=cores_barras)

        eixo.axhline(0, color=COR_TEXTO_SECUNDARIO, linewidth=0.8)
        eixo.tick_params(colors=COR_TEXTO, labelsize=9)
        eixo.set_ylabel("R$", color=COR_TEXTO, fontsize=9)
        eixo.spines["top"].set_visible(False)
        eixo.spines["right"].set_visible(False)
        eixo.spines["left"].set_color(COR_TEXTO_SECUNDARIO)
        eixo.spines["bottom"].set_color(COR_TEXTO_SECUNDARIO)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        anotacao = eixo.annotate(
            "", xy=(0, 0), xytext=(0, 12), textcoords="offset points", ha="center",
            bbox=dict(boxstyle="round,pad=0.4", fc=COR_CARD_CLARO, ec=COR_ACCENT),
            color=COR_TEXTO, fontsize=9, fontweight="bold"
        )
        anotacao.set_visible(False)

        def ao_mover_mouse(evento):
            if evento.inaxes != eixo:
                if anotacao.get_visible():
                    anotacao.set_visible(False)
                    canvas.draw_idle()
                return
            for i, barra in enumerate(barras):
                contem, _ = barra.contains(evento)
                if contem:
                    altura = barra.get_height()
                    anotacao.xy = (barra.get_x() + barra.get_width() / 2, altura)
                    anotacao.set_text(f"R$ {altura:.2f} ({percentuais[i]:+.1f}%)")
                    anotacao.set_visible(True)
                    canvas.draw_idle()
                    return
            if anotacao.get_visible():
                anotacao.set_visible(False)
                canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", ao_mover_mouse)

    # ---------- AÇÕES ----------

    def _abrir_cadastro(self):
        janela = TelaCadastroOperacao(self, ao_salvar=self._carregar_tudo)
        janela.grab_set()