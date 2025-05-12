# TCC do curso de Tecnologia em Análise e Desenvolvimento de sistemas do IFSUL - Câmpus Bagé

## Como rodar o projeto

# Tutorial de Instalação e Execução de um Projeto Django

Este guia fornece instruções passo a passo para configurar e executar um projeto Django, garantindo um ambiente de desenvolvimento limpo e funcional.

## Pré-requisitos

- Python 3.x instalado
- Conhecimentos básicos de linha de comando

## Configuração do Ambiente

### 1. Criação do Ambiente Virtual

Ambientes virtuais isolam as dependências do projeto, evitando conflitos com outros pacotes Python instalados no sistema.

```bash
python3 -m venv venv
```

### 2. Ativação do Ambiente Virtual

**Windows:**

```bash
.\venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

> **Nota:** Quando ativado com sucesso, o nome do ambiente virtual (venv) aparecerá no início da linha de comando.

### 3. Instalação das Dependências

```bash
pip install -r requirements.txt
```

## Configuração do Banco de Dados

O projeto utiliza SQLite 3 como banco de dados padrão para desenvolvimento, facilitando a configuração inicial. Este pode ser substituído por qualquer outro banco de dados relacional em ambiente de produção.

```bash
python manage.py migrate
```

Este comando cria as tabelas necessárias no banco de dados baseado nas migrações definidas no projeto.

## Iniciando o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Por padrão, o servidor Django será iniciado na porta 8000. Acesse o aplicativo em seu navegador através do endereço:

```
http://127.0.0.1:8000/
```

## Próximos Passos

- Crie um usuário para acessar a aplicação:

## Solução de Problemas Comuns

- **Erro na instalação de pacotes**: Verifique se seu ambiente virtual está ativado
- **Erro na migração**: Certifique-se de que o banco de dados está configurado corretamente
- **Servidor não inicia**: Verifique se a porta 8000 não está sendo usada por outro processo

---

Para desenvolvedores que desejam contribuir para o projeto, consulte a documentação completa do Django em [djangoproject.com](https://www.djangoproject.com/documentation/).

## TODO LIST V1

[X] - Cadastro de cursos \
[X] - Cadastro de aulas (em formato de vídeo) \
[X] - Sistema de login \
[X] - Matrícula em curso \
[X] - Lista de meus cursos \
[X] - Player de vídeo com opção de concluir aulas
