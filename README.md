# Caronas Universitárias API

API REST para organizar caronas entre alunos da faculdade. Um aluno pode oferecer viagens como motorista e também reservar vagas como passageiro.

Projeto da disciplina **Megadados** (Insper), desenvolvido com **FastAPI**, **SQLModel** (ORM) e **MySQL**.

## Como executar

1. Crie e ative um ambiente virtual e instale as dependências:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Crie o banco no MySQL:

   ```sql
   CREATE DATABASE caronas;
   ```

3. Copie `.env.example` para `.env` e preencha com suas credenciais do MySQL.

4. Inicie a API:

   ```bash
   fastapi dev app/main.py
   ```
