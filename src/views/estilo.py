# src/views/estilo.py
import customtkinter as ctk

# fundo
COR_FUNDO = "#0B0B0E"
COR_CARD = "#17171C"
COR_CARD_CLARO = "#1F1F26"
COR_BORDA = "#2A2A32"

# texto
COR_TEXTO = "#F5F5F3"
COR_TEXTO_SECUNDARIO = "#A0A0AA"

# linhas de tabela
COR_LINHA_PAR = "#17171C"
COR_LINHA_IMPAR = "#1D1D24"
COR_LINHA_SELECIONADA = "#332C55"

# accent
COR_ACCENT = "#8B7FF0"
COR_ACCENT_HOVER = "#7568DD"

# semânticas
COR_LUCRO = "#3ED68C"
COR_PREJUIZO = "#F26E62"
COR_COMPRA = "#3ED68C"
COR_VENDA = "#F26E62"

CORES_GRAFICO = ["#8B7FF0", "#3ED68C", "#F0AC5C", "#5CA9F0", "#F26E62", "#E063B8"]

# fontes
FONTE_TITULO = ("Segoe UI", 26, "bold")
FONTE_SUBTITULO = ("Segoe UI", 14, "bold")
FONTE_LABEL = ("Segoe UI", 13, "bold")
FONTE_BOTAO = ("Segoe UI", 13, "bold")
FONTE_TABELA = ("Segoe UI", 12, "bold")
FONTE_TABELA_CABECALHO = ("Segoe UI", 11, "bold")
FONTE_TOTAL = ("Segoe UI", 20, "bold")
FONTE_INPUT = ("Segoe UI", 13, "bold")

PADDING_CARD = 24
PADDING_JANELA = 28


def configurar_tema():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")