from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def conectar():
    return sqlite3.connect("banco.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT
        )
    """)

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        c.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        conn.commit()
        conn.close()
        return redirect("/clientes")

    c.execute("SELECT * FROM clientes")
    lista_clientes = c.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=lista_clientes)

@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            assunto TEXT,
            descricao TEXT,
            data TEXT,
            status TEXT
        )
    """)

    c.execute("SELECT id, nome FROM clientes")
    clientes = c.fetchall()

    if request.method == "POST":
        c.execute(
            "INSERT INTO atendimentos (cliente_id, assunto, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)",
            (
                request.form["cliente"],
                request.form["assunto"],
                request.form["descricao"],
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Aberto"
            )
        )
        conn.commit()
        conn.close()
        return redirect("/atendimentos")

    c.execute("""
        SELECT atendimentos.id, clientes.nome, assunto, status, data
        FROM atendimentos
        JOIN clientes ON clientes.id = atendimentos.cliente_id
        ORDER BY atendimentos.id DESC
    """)
    lista_atendimentos = c.fetchall()
    conn.close()

    return render_template(
        "atendimentos.html",
        atendimentos=lista_atendimentos,
        clientes=clientes
    )

@app.route("/concluir/<int:id>")
def concluir(id):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE atendimentos SET status='Concluído' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/atendimentos")

if __name__ == "__main__":
    app.run()
