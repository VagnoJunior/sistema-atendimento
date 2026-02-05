from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Sistema de Atendimento ONLINE"
