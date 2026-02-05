from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# ===== CONFIGURAÇÃO DO BANCO (PRODUÇÃO OK) =====

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "banco.db")

def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        telefone TEXT,
        email TEXT
    )
    """)

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

    conn.commit()
    conn.close()

criar_banco()

# ===== ROTAS =====

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        c.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (
                request.form["nome"],
                request.form["telefone"],
                request.form["email"]
            )
        )
        conn.commit()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()
    conn.close()

    return render_template("clientes.html", clientes=clientes)

@app.route("/cliente/<int:id>")
def historico_cliente(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT nome FROM clientes WHERE id=?", (id,))
    cliente = c.fetchone()

    c.execute("""
        SELECT assunto, status, data
        FROM atendimentos
        WHERE cliente_id=?
        ORDER BY id DESC
    """, (id,))

    atendimentos = c.fetchall()
    conn.close()

    return render_template(
        "historico.html",
        cliente=cliente,
        atendimentos=atendimentos
    )

@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    busca = request.args.get("busca", "")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    if request.method == "POST":
        c.execute("""
            INSERT INTO atendimentos
            (cliente_id, assunto, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["cliente"],
            request.form["assunto"],
            request.form["descricao"],
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Aberto"
        ))
        conn.commit()

    c.execute("""
        SELECT atendimentos.id, clientes.id, clientes.nome, assunto, status, data
        FROM atendimentos
        JOIN clientes ON clientes.id = atendimentos.cliente_id
        WHERE clientes.nome LIKE ? OR assunto LIKE ?
        ORDER BY atendimentos.id DESC
    """, (f"%{busca}%", f"%{busca}%"))

    atendimentos = c.fetchall()
    conn.close()

    return render_template(
        "atendimentos.html",
        clientes=clientes,
        atendimentos=atendimentos,
        busca=busca
    )

@app.route("/concluir/<int:id>")
def concluir(id):
    conn = conectar()
    c = conn.cursor()
    c.execute(
        "UPDATE atendimentos SET status='Concluído' WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/atendimentos")
