from flask import Flask, render_template
import mysql.connector as my

def conectar_banco():
    config = { 
    'user': 'root', 
    'password': '1234', 
    'host': 'localhost', 
    'database': 'SuperSelect_sa', 
    }
    conexao = my.connect(**config)
    return conexao

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login ")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)