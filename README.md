# OS Manager (Sistema de Gerenciamento de Ordens de Serviço)

Um sistema de desktop simples para gerenciamento de Ordens de Serviço (OS), desenvolvido em Python com interface gráfica utilizando a biblioteca Flet. Ideal para pequenas empresas ou técnicos autônomos que precisam organizar seus serviços e clientes.

## ✨ Funcionalidades Principais

*   **Gerenciamento de Clientes:** Cadastro, Edição, Visualização e Exclusão de clientes.
*   **Gerenciamento de Tipos de Serviço:** Cadastro, Edição, Visualização e Exclusão de tipos de serviço oferecidos.
*   **Gerenciamento de Ordens de Serviço:**
    *   Criação, Atualização, Visualização e Exclusão de OS.
    *   Associação de Clientes e Tipos de Serviço às OS.
    *   Registro de descrição do problema, endereço do serviço, garantia, status, valor, etc.
    *   Upload e visualização de foto relacionada à OS.
    *   Geração automática de número sequencial para novas OS.
*   **Relatórios:** Geração de relatórios de OS em formato PDF, com filtros por cliente, status e período (data de entrada).
*   **Interface Gráfica:** Interface de usuário construída com Flet, proporcionando uma experiência de desktop moderna.
*   **Persistência de Dados:** Armazenamento local dos dados em um banco de dados SQLite (`os_database.db`).

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.x
*   **Interface Gráfica:** [Flet](https://flet.dev/)
*   **Banco de Dados:** SQLite 3
*   **Geração de PDF:** [ReportLab](https://www.reportlab.com/)
*   **Manipulação de Imagens:** [Pillow (PIL Fork)](https://python-pillow.org/)

## ⚙️ Pré-requisitos

*   [Python 3](https://www.python.org/downloads/) (Recomendado 3.9 ou superior)
*   [Git](https://git-scm.com/downloads/) (para clonar o repositório)
*   `pip` (gerenciador de pacotes Python, geralmente vem com o Python)

## 🚀 Instalação e Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```
    *(Substitua `seu-usuario/seu-repositorio` pelo URL real do seu repositório no GitHub)*

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    *   Isso isola as dependências do projeto.
    ```bash
    # No Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as Dependências:**
    *   Certifique-se de que você tem um arquivo `requirements.txt` atualizado (veja nota abaixo).
    ```bash
    pip install -r requirements.txt
    ```
    *   **Nota:** Se você ainda não tem um `requirements.txt`, gere-o (com o ambiente virtual ativo):
        ```bash
        pip freeze > requirements.txt
        ```
        *Não se esqueça de adicionar (`git add requirements.txt`) e commitar (`git commit -m "Add requirements.txt"`) este arquivo!*

4.  **Banco de Dados:**
    *   O banco de dados SQLite (`os_database.db`) e suas tabelas são criados automaticamente na pasta raiz do projeto durante a primeira execução do script principal (ou pela função `setup_database()`), caso ainda não existam.
    *   Os diretórios `uploads` (para fotos) e `reports` (para PDFs temporários) também são criados automaticamente.

## ▶️ Executando a Aplicação

1.  **Certifique-se de que o ambiente virtual está ativado.**
2.  **Execute o script principal:**
    ```bash
    python main.py
    ```
    *(Se o seu script principal tiver outro nome, como `app.py`, use esse nome no comando)*

##  Ecrãs

*(Opcional, mas altamente recomendado)*

*Adicione aqui algumas capturas de tela da sua aplicação para dar uma ideia visual.*

Exemplo:
`![Tela Principal](link/para/screenshot_main.png)`
`![Tela de Cadastro de OS](link/para/screenshot_os_form.png)`

## 📄 Licença

*(Opcional, mas recomendado)*

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes (se você adicionar um).

Exemplo simples: "Distribuído sob a Licença MIT."

## 🤝 Contribuição

*(Opcional)*

Contribuições são bem-vindas! Se você tiver sugestões ou encontrar problemas, por favor, abra uma *issue* no repositório do GitHub.

## 📧 Contato

*(Opcional)*

Seu Nome / Nome da Empresa - seu.email@exemplo.com

Link do Projeto: [https://github.com/seu-usuario/seu-repositorio](https://github.com/seu-usuario/seu-repositorio)
