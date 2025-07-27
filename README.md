# SEMAPA3 - Sistema de Gestão Municipal de Árvores e Podas

## 🌳 Sobre o Projeto

O SEMAPA3 é uma **refatoração completa** do sistema original SEMAPA, transformando uma aplicação monolítica em uma **arquitetura modular e escalável** baseada em Clean Architecture.

## 🏗️ Arquitetura

O sistema foi completamente reestruturado seguindo as melhores práticas:

- **Clean Architecture**: Separação clara de responsabilidades
- **Modular Design**: Fácil adição de novos módulos
- **MVC Pattern**: Controllers, Services e Models bem definidos
- **Blueprint System**: Organização modular das rotas
- **Service Layer**: Lógica de negócio isolada e reutilizável

## 📁 Estrutura do Projeto

```
semapa3/
├── app.py                 # Application Factory
├── run.py                 # Arquivo principal de execução
├── requirements.txt       # Dependências
├── config/
│   └── settings.py       # Configurações centralizadas
├── core/                 # Núcleo da aplicação
│   ├── database.py       # Configuração do banco
│   ├── security.py       # Autenticação e autorização
│   └── exceptions.py     # Tratamento de erros
├── models/               # Modelos de dados
│   ├── user_model.py
│   ├── requerente_model.py
│   ├── especie_model.py
│   ├── arvore_model.py
│   ├── requerimento_model.py
│   ├── ordem_model.py
│   └── vistoria_model.py
├── services/             # Lógica de negócio
│   ├── auth_service.py
│   ├── requerente_service.py
│   ├── arvore_service.py
│   └── requerimento_service.py
├── controllers/          # Controllers (Views)
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   └── requerente_controller.py
├── templates/            # Templates HTML
├── static/              # CSS, JS, imagens
└── tests/               # Testes automatizados
```

## 🚀 Como Executar

### 1. Instalação

```bash
# Clone o projeto
git clone <seu-repositorio>
cd semapa3

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Configure as variáveis de ambiente (opcional)
export SECRET_KEY="sua-chave-secreta"
export DEBUG=True
```

### 3. Execução

```bash
# Execute a aplicação
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🔧 Funcionalidades

- ✅ **Autenticação e Autorização** por níveis de usuário
- ✅ **Gestão de Requerentes** (PF e PJ)
- ✅ **Cadastro de Espécies** de árvores
- ✅ **Gerenciamento de Árvores** com geolocalização
- ✅ **Sistema de Requerimentos** (poda, remoção, transplante)
- ✅ **Ordens de Serviço** automatizadas
- ✅ **Vistorias Técnicas** com upload de fotos
- ✅ **Geração de KML** para visualização em mapas
- ✅ **Dashboard Administrativo** com estatísticas
- ✅ **Sistema de Relatórios**

## 🛡️ Segurança

- Autenticação com Flask-Login
- Proteção CSRF com Flask-WTF
- Hash seguro de senhas com Werkzeug
- Controle de acesso por níveis (user, técnico, admin, super_admin)
- Validação de dados com WTForms

## 📊 Banco de Dados

O sistema utiliza SQLAlchemy ORM com suporte a:
- SQLite (desenvolvimento)
- PostgreSQL (produção)
- MySQL (produção)

### Migração dos Dados

O sistema mantém **total compatibilidade** com a base de dados existente. A migração é automática ao executar a aplicação.

## 🧪 Testes

```bash
# Execute os testes
python -m pytest tests/
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para dúvidas e suporte, entre em contato com a equipe de desenvolvimento.

---

**SEMAPA3** - Sistema modular, escalável e preparado para o futuro! 🚀
