# src/main.py
from database.conexao import criar_tabelas
from views.tela_principal import TelaPrincipal


def main():
    criar_tabelas()
    app = TelaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()