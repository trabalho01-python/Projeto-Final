from flask import Flask, render_template, request, redirect, flash, session
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
app.secret_key = "1234"

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
        session['usuario'] = usuario
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
        cpf = request.form['cpf']

        #Criptografar a senha
        senha_bytes = senha.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')

        endereco = request.form.get('endereco')

        #Conectar banco
        conexao = conectar_banco()
        cursor = conexao.cursor()

        try:
            cursor.execute("""  INSERT INTO usuarios (nome, email, senha, tipo, cpf, endereco) VALUES (%s,%s,%s,%s,%s,%s) """, (nome, email, senha_hash, tipo, cpf, endereco))
            conexao.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect('/login')
        
        except Exception as erro:
            conexao.rollback()
            flash(f'Ocorreu um erro ao cadastrar: {str(erro)}', 'danger')

        finally:
            cursor.close()
            conexao.close()

    return render_template('/cadastro.html', tipo=tipo)


@app.route('/usuario')
def usuario():
    usuario = session.get('usuario')
    if not usuario:
        return redirect('/login')
    if usuario['tipo'] != 'usuario':
        return redirect('/login')
    
    return render_template('usuario.html')

@app.route('/administrador')
def administrador():
    # usuario = session.get('usuario')
    # if not usuario:
    #     return redirect('/login')
    # if usuario['tipo'] != 'administrador':
    #     return redirect('/login')

    return render_template('administrador.html')

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco = request.form['preco'].replace('.', '').replace(',', '.')
        data_validade = request.form['data_validade']
        estoque = request.form['estoque']
        sem_validade = 'sem_validade' in request.form
        data_validade = None if sem_validade else request.form['data_validade']
        imagem = request.files['imagem']

        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = "INSERT INTO produtos (nome, descricao, categoria, preco, data_validade, estoque, sem_validade, imagem) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        valores = (nome, descricao, categoria, preco, data_validade, estoque, sem_validade, imagem)

        try:
            cursor.execute(sql, valores)
            conexao.commit()
            flash('Produto cadastrado com sucesso!', 'success')
        except Exception as e:
            conexao.rollback()
            flash(f'Erro ao cadastrar produto: {e}', 'danger')

        return redirect('/cadastrar_produto')

    return render_template('cadastrar_produto.html')


@app.route('/consultar_produto', methods=['GET', 'POST'])
def consultar_produto():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM produtos
        ORDER BY id DESC
    """)
    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()
    return render_template('consultar_produto.html', produtos=produtos)


@app.route('/excluir-produto/<int:id>')
def excluir_produto(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conexao.commit()
    flash('Produto excluído com sucesso!', 'success')
    return redirect('consultar_produto')

@app.route('/editar-produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco = request.form['preco'].replace('.', '').replace(',', '.')
        estoque = request.form['estoque']
        sem_validade = 'sem_validade' in request.form
        data_validade = None if sem_validade else request.form['data_validade']

        cursor.execute("""
            UPDATE produtos SET nome=%s, descricao=%s, categoria=%s, preco=%s, data_validade=%s, estoque=%s
            WHERE id=%s
        """, (nome, descricao, categoria, preco, data_validade, estoque, id))
        conexao.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect('consultar_produto')

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()
    return render_template('editar_produto.html', produto=produto)


if __name__ == "__main__":
    app.run(debug=True)