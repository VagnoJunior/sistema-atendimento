from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "minha_chave_secreta"

# ---------------- Banco de Dados ----------------
def conectar():
    banco = "banco.db"
    conn = sqlite3.connect(banco)
    return conn

# ---------------- Login ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email=? AND senha=?", (email, senha))
        usuario = c.fetchone()
        conn.close()

        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            return redirect("/")
        else:
            return render_template("login.html", erro="Email ou senha inválidos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def logado():
    return "usuario_id" in session

# ---------------- Home / Dashboard ----------------
@app.route("/")
def index():
    if not logado():
        return redirect("/login")
    return render_template("index.html", nome=session["usuario_nome"])

# ---------------- Clientes ----------------
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if not logado():
        return redirect("/login")

    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        email = request.form["email"]
        c.execute("INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)", (nome, telefone, email))
        conn.commit()

    c.execute("SELECT * FROM clientes")
    lista_clientes = c.fetchall()
    conn.close()
    return render_template("clientes.html", clientes=lista_clientes)

# ---------------- Histórico do Cliente ----------------
@app.route("/cliente/<int:id>")
def cliente_historico(id):
    if not logado():
        return redirect("/login")

    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = c.fetchone()

    c.execute("SELECT * FROM atendimentos WHERE cliente_id=? ORDER BY data DESC", (id,))
    atendimentos = c.fetchall()
    conn.close()

    return render_template("cliente_historico.html", cliente=cliente, atendimentos=atendimentos)

# ---------------- Atendimentos ----------------
@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    if not logado():
        return redirect("/login")

    conn = conectar()
    c = conn.cursor()

    # Cadastro novo atendimento
    if request.method == "POST":
        cliente_id = request.form["cliente"]
        assunto = request.form["assunto"]
        descricao = request.form["descricao"]
        data = request.form["data"]
        status = "Aberto"
        c.execute("INSERT INTO atendimentos (cliente_id, assunto, descricao, data, status) VALUES (?, ?, ?, ?, ?)",
                  (cliente_id, assunto, descricao, data, status))
        conn.commit()

    # Buscar atendimentos
    busca = request.args.get("busca", "")
    if busca:
        c.execute("""SELECT a.id, cl.nome, a.assunto, a.status, a.data 
                     FROM atendimentos a JOIN clientes cl ON a.cliente_id = cl.id
                     WHERE cl.nome LIKE ? OR a.assunto LIKE ?
                     ORDER BY a.data DESC""", (f"%{busca}%", f"%{busca}%"))
    else:
        c.execute("""SELECT a.id, cl.nome, a.assunto, a.status, a.data 
                     FROM atendimentos a JOIN clientes cl ON a.cliente_id = cl.id
                     ORDER BY a.data DESC""")
    lista_atendimentos = c.fetchall()

    # Lista de clientes para o select
    c.execute("SELECT * FROM clientes")
    lista_clientes = c.fetchall()

    conn.close()
    return render_template("atendimentos.html", atendimentos=lista_atendimentos, clientes=lista_clientes, busca=busca)

# ---------------- Concluir Atendimento ----------------
@app.route("/concluir/<int:id>")
def concluir(id):
    if not logado():
        return redirect("/login")
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE atendimentos SET status='Concluído' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/atendimentos")

# ---------------- Rodar App ----------------
if __name__ == "__main__":
    if not os.path.exists("banco.db"):
        # criar banco automaticamente se não existir
        conn = sqlite3.connect("banco.db")
        c = conn.cursor()
        # tabela usuarios
        c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        email TEXT,
                        senha TEXT
                    )""")
        # tabela clientes
        c.execute("""CREATE TABLE IF NOT EXISTS clientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        telefone TEXT,
                        email TEXT
                    )""")
        # tabela atendimentos
        c.execute("""CREATE TABLE IF NOT EXISTS atendimentos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER,
                        assunto TEXT,
                        descricao TEXT,
                        data TEXT,
                        status TEXT
                    )""")
        # usuário admin inicial
        c.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                  ("Administrador", "admin@admin.com", "123"))
        conn.commit()
        conn.close()
    app.run(debug=True)
