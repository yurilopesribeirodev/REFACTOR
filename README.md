# Carteira de Ativos

Sistema de gerenciamento de carteira de ações, desenvolvido para a disciplina de POO.

## Tecnologias
- Python 3.13
- SQLite (nativo do Python)
- CustomTkinter (interface gráfica)
- Matplotlib (gráficos)
- Requests (consulta de cotações via API)

## Como rodar

### 1. Clone o repositório
\`\`\`bash
git clone https://github.com/yurilopesribeirodev/carteira-ativos
cd PROJETO
\`\`\`

### 2. Crie e ative um ambiente virtual
\`\`\`bash
python -m venv venv
\`\`\`

No Windows (PowerShell):
\`\`\`bash
venv\Scripts\Activate.ps1
\`\`\`

No Linux/Mac:
\`\`\`bash
source venv/bin/activate
\`\`\`

### 3. Instale as dependências
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Rode o programa
\`\`\`bash
cd src
python main.py
\`\`\`

O banco de dados (\`carteira.db\`) é criado automaticamente na primeira execução, na raiz do projeto.

## Estrutura do projeto
\`\`\`
src/
├── models/         # classes de domínio (Ativo, Operacao, Posicao, Carteira)
├── repositories/   # acesso ao banco SQLite
├── services/       # integração com API externa de cotações
├── views/          # interface gráfica (tkinter/customtkinter)
├── database/       # conexão e schema do banco
└── main.py         # ponto de entrada
\`\`\`