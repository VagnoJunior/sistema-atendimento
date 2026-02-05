from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DB = "banco.db"

def conectar():
    return sqlite3.connect(DB)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        c.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        conn.commit()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)

@app.route("/cliente/<int:id>")
def cliente(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = c.fetchone()

    c.execute(
        "SELECT assunto, data, status FROM atendimentos WHERE cliente_id=?",
        (id,)
    )
    atendimentos = c.fetchall()

    conn.close()

    return render_template(
        "cliente_historico.html",
        cliente=cliente,
        atendimentos=atendimentos
    )

@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        assunto = request.form["assunto"]
        descricao = request.form["descricao"]
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        status = "Aberto"

        c.execute("""
            INSERT INTO atendimentos
            (cliente_id, assunto, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (cliente_id, assunto, descricao, data, status))
        conn.commit()

    c.execute("""
        SELECT a.id, c.nome, a.assunto, a.status, a.data
        FROM atendimentos a
        JOIN clientes c ON a.cliente_id = c.id
        ORDER BY a.id DESC
    """)
    atendimentos = c.fetchall()

    c.execute("SELECT id, nome FROM clientes")
    clientes = c.fetchall()

    conn.close()

    return render_template(
        "atendimentos.html",
        atendimentos=atendimentos,
        clientes=clientes
    )

if __name__ == "__main__":
    app.run()
