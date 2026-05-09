from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "123456"

# =========================
# BANCO SQLITE
# =========================

def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        senha TEXT,
        tipo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estagiarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT
    )
    """)

    # usuários padrão
    cursor.execute("SELECT * FROM usuarios")
    if not cursor.fetchall():
        cursor.execute("INSERT INTO usuarios VALUES (NULL,'diretoria','123','Diretoria')")
        cursor.execute("INSERT INTO usuarios VALUES (NULL,'estagiario','123','Estagiario')")

    conn.commit()
    conn.close()

criar_banco()

# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT tipo FROM usuarios
        WHERE usuario=? AND senha=?
        """, (usuario, senha))

        user = cursor.fetchone()
        conn.close()

        if user:
            session["tipo"] = user[0]

            if user[0] == "Diretoria":
                return redirect("/diretoria")
            else:
                return redirect("/estagiario")

    return render_template("login.html")

# =========================
# ESTAGIÁRIO (SÓ INSERE)
# =========================

@app.route("/estagiario", methods=["GET", "POST"])
def estagiario():

    if session.get("tipo") != "Estagiario":
        return redirect("/")

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO estagiarios (nome, email)
        VALUES (?, ?)
        """, (nome, email))

        conn.commit()
        conn.close()

    return render_template("estagiario.html")

# =========================
# DIRETORIA (VER TUDO)
# =========================

@app.route("/diretoria")
def diretoria():

    if session.get("tipo") != "Diretoria":
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM estagiarios")
    dados = cursor.fetchall()

    conn.close()

    return render_template("diretoria.html", dados=dados)

# =========================
# EXECUTAR
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)