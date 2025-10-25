from flask import Flask, render_template, request, redirect, flash
import mysql.connector as my
import bcrypt

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
app.secret_key = "chave_secreta"

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha'].encode('utf-8')

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            if bcrypt.checkpw(senha, usuario['senha'].encode('utf-8')):
                if usuario['tipo'] == 'administrador':
                    return redirect('/administrador')
                else:
                    return redirect('/usuario')
            else:
                error = "Senha incorreta."
        else:
            error = "E-mail não encontrado."

    return render_template('login.html', error=error)

@app.route('/cadastro', methods = ['GET','POST'])
def cadastro():
    tipo = "" #valor padrão
    
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        #Criptografar a senha
        senha_bytes = senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')

        cpf = request.form.get('cpf')
        endereco = request.form.get('endereco')

        # #Se for adm
        # if tipo == 'administrador':
        #     cpf = request.form['cpf']
        #     endereco = request.form['endereco']

        #Conectar banco
        banco = conectar_banco()
        cursor = banco.cursor()

        try:
            cursor.execute("""  INSERT INTO usuarios (nome, email, senha, tipo, cpf, endereco) VALUES (%s,%s,%s,%s,%s,%s) """, (nome, email, senha_hash, tipo, cpf, endereco))
            banco.commit()
            flash("Cadastro realizado com sucesso!", "sucess")
            return redirect('/cadastro')
        
        except Exception as erro:
            banco.rollback()
            flash(f'Ocorreu um erro ao cadastrar: {str(erro)}', 'danger')

        finally:
            cursor.close()
            banco.close()

    return render_template('/cadastro.html', tipo=tipo)


@app.route('/usuario')
def usuario():
    return render_template('usuario.html')

@app.route('/administrador')
def administrador():
    return render_template('administrador.html')



if __name__ == "__main__":
    app.run(debug=True)