from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta_simples"

DB = "banco.db"

def conectar():
    return sqlite3.connect(DB)

def logado():
    return "usuario_id" in session

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        c = conn.cursor()
        c.execute(
            "SELECT id, nome FROM usuarios WHERE email=? AND senha=?",
            (email, senha)
        )
        usuario = c.fetchone()
        conn.close()

        if usuario:
            session["usuario_id"] = usuario[0]
            session["usuario_nome"] = usuario[1]
            return redirect("/")
        else:
            return render_template("login.html", erro="Login inválido")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- HOME ----------
@app.route("/")
def index():
    if not logado():
        return redirect("/login")
    return render_template("index.html", usuario=session["usuario_nome"])

# ---------- CLIENTES ----------
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if not logado():
        return redirect("/login")

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
def cliente(id):
    if not logado():
        return redirect("/login")

    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM clientes WHERE id=?", (id,))
    cliente = c.fetchone()

    c.execute(
        "SELECT assunto, descricao, data, status FROM atendimentos WHERE cliente_id=?",
        (id,)
    )
    atendimentos = c.fetchall()

    conn.close()

    return render_template(
        "cliente_historico.html",
        cliente=cliente,
        atendimentos=atendimentos
    )

# ---------- ATENDIMENTOS ----------
@app.route("/atendimentos", methods=["GET", "POST"])
def atendimentos():
    if not logado():
        return redirect("/login")

    conn = conectar()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("""
            INSERT INTO atendimentos
            (cliente_id, assunto, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["cliente_id"],
            request.form["assunto"],
            request.form["descricao"],
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Aberto"
        ))
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
