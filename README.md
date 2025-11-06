# 🐍 WP-Dashboard-Python-Bootstrap

Um painel administrativo customizado para WordPress construído com Flask (Python) para o backend e Bootstrap 5 para o frontend. Este projeto utiliza a API REST do WordPress para realizar operações CRUD (Criar, Ler, Atualizar, Deletar) e implementa um sistema de cache em XML.

## 🚀 Funcionalidades

* **Frontend Moderno:** Interface responsiva construída com Bootstrap 5.
* **CRUD Completo:** Crie, visualize, edite e delete posts diretamente do painel Python.
* **Cache XML:** Resiliência contra falhas na API do WordPress. Se a API estiver inacessível, os dados são carregados do cache local em XML.
* **Autenticação Segura:** Utiliza Basic Auth com Senhas de Aplicação do WordPress.

## ⚙️ Pré-requisitos

Para rodar este projeto, você precisará de:

1.  **Python 3.x** instalado.
2.  Um ambiente de teste **WordPress** rodando (localmente ou online).
3.  Uma **Senha de Aplicação** gerada no seu painel WordPress (WP Admin > Usuários > Seu Usuário).

## 💻 Instalação e Configuração

### 1. Clonar o Repositório

```bash
git clone [https://github.com/SEU-USUARIO/nome-do-repositorio](https://github.com/SEU-USUARIO/nome-do-repositorio)
cd nome-do-repositorio
````

### 2\. Instalar Dependências

Crie um ambiente virtual e instale as bibliotecas necessárias:

```bash
python -m venv venv
source venv/bin/activate  # No Windows use: .\venv\Scripts\activate
pip install Flask requests
```

### 3\. Configurar Credenciais (Arquivo `app.py`)

Abra o arquivo `app.py` e substitua os placeholders pelas suas credenciais e URL do WordPress. **Isso é crucial para o funcionamento do CRUD.**

```python
# app.py
WP_URL = '[http://seu-site-wordpress.com/wp-json/wp/v2](http://seu-site-wordpress.com/wp-json/wp/v2)'
WP_USERNAME = "seu_usuario_api"
WP_APP_PASSWORD = "sua_senha_de_aplicacao" 
```

### 4\. Estrutura de Pastas

Certifique-se de que a pasta `templates` esteja na raiz do projeto, contendo os arquivos: `base.html`, `dashboard.html` e `post_form.html`.

### 5\. Executar a Aplicação

Inicie o servidor Flask:

```bash
python app.py
```

Acesse a aplicação no seu navegador (geralmente em `http://127.0.0.1:5000`).

## ⚠️ Teste de Cache XML

Para testar a funcionalidade de cache:

1.  Execute a aplicação pela primeira vez para que ela crie o arquivo `data/posts_cache.xml`.
2.  Interrompa a aplicação (`Ctrl+C`).
3.  Altere a `WP_URL` em `app.py` para um valor incorreto (simulando uma falha de conexão).
4.  Execute a aplicação novamente. Ela deverá carregar os posts do arquivo XML e mostrar uma mensagem de aviso.

-----

## 📄 Estrutura do Projeto

```
my_wp_dashboard/
├── venv/                   # Ambiente Virtual
├── data/                   # Pasta para arquivos de cache
│   └── posts_cache.xml     # Cache dos posts
├── templates/              # Arquivos HTML Jinja2/Bootstrap
│   ├── base.html
│   ├── dashboard.html
│   └── post_form.html
├── app.py                  # Lógica principal (Flask, CRUD, API e XML)
└── README.md               # Este arquivo
```
