# Automação Publicador de Arquivos PBIX no Power BI com Interface Gráfica

Este projeto é uma aplicação em Python com interface gráfica (Tkinter) que permite a publicação de arquivos `.pbix` no Power BI de forma automatizada. O sistema realiza login, busca workspaces e datasets, publica os arquivos, atualiza os parâmetros de conexão e inicia o processo de atualização dos dados.

## 🔧 Funcionalidades

- Login automatizado no Power BI via OAuth2
- Busca de **Workspaces** e **Datasets**
- Seleção e publicação de arquivos `.pbix`
- Renomeia os arquivos com o nome do dataset selecionado
- Captura e restaura os parâmetros (ex: `SERVIDOR` e `BANCO`)
- Atualiza os parâmetros no novo dataset
- Inicia o processo de atualização automática do dataset após a publicação
- Interface gráfica amigável e funcional com Tkinter

## 🖼️ Interface

A interface gráfica foi desenvolvida com **Tkinter**, oferecendo uma experiência prática para os usuários:

- Dropdown para selecionar workspace
- Lista de checkboxes para selecionar datasets
- Botões para executar cada etapa do processo

## ⚙️ Tecnologias Utilizadas

- **Python 3.x**
- **Tkinter** (interface gráfica)
- **Requests** (requisições HTTP para API do Power BI)
- **API REST do Power BI**

## 🚨 Aviso de Segurança

⚠️ **Este projeto não contém credenciais reais.**  
Todos os campos de autenticação (`client_id`, `client_secret`, `username`, `password`, etc.) foram propositalmente substituídos por placeholders e **não devem ser preenchidos com credenciais reais em repositórios públicos.**  
Se for utilizar este projeto com suas próprias credenciais, faça isso com cautela e evite expô-las em qualquer lugar público.

Recomenda-se usar variáveis de ambiente ou arquivos `.env` (com uso da biblioteca `python-dotenv`) para manter as credenciais protegidas.

## 🧪 Como Usar

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/Automa-oPowerBI-API.git
   cd Automa-oPowerBI-API
   ```

2. Instale os requisitos (se houver):
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o script:
   ```bash
   python nome_do_arquivo.py
   ```

4. Faça login e siga as etapas pela interface para publicar seu arquivo `.pbix`.

## 📁 Estrutura Sugerida de Arquivos

```
├── venv
├── main.py
├── README.md
└── requirements.txt (opcional)
```

## 🙋 Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de facilitar o processo de publicação e atualização de relatórios no Power BI em ambientes corporativos, oferecendo uma solução automatizada e de fácil uso para equipes de dados.
