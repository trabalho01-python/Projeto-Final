from flask import Flask, render_template, request, redirect, flash, session, jsonify
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
        senha = request.form['senha'].encode('utf-8')  # senha digitada

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario:
            # Confere se a senha digitada bate com a senha hash do banco
            if bcrypt.checkpw(senha, usuario['senha'].encode('utf-8')):
                # Armazena apenas informações seguras na sessão
                session['usuario_id'] = usuario['id']
                session['usuario_email'] = usuario['email']
                session['usuario_tipo'] = usuario['tipo']
                print("Sessão após login:", dict(session))

                # Redireciona conforme o tipo de usuário
                if usuario['tipo'] == 'administrador':
                    return redirect('/administrador')
                else:
                    return redirect('/cliente')
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
            return redirect('/login')
        
        except Exception as erro:
            conexao.rollback()
            flash(f'Ocorreu um erro ao cadastrar: {str(erro)}', 'danger')

        finally:
            cursor.close()
            conexao.close()

    return render_template('/cadastro.html', tipo=tipo)



@app.route('/cliente')
def cliente():
    print("Sessão atual:", dict(session))  # debug
    usuario_id = session.get('usuario_id')
    usuario_tipo = session.get('usuario_tipo')
    usuario_email = session.get('usuario_email')

    if not usuario_id or usuario_tipo != 'cliente':
        print("Redirecionando para login")  # debug
        return redirect('/login')
    
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos") 
    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('cliente.html', email=usuario_email, produtos=produtos)


@app.route('/administrador')
def administrador():
    usuario_id = session.get('usuario_id')
    usuario_tipo = session.get('usuario_tipo')
    usuario_email = session.get('usuario_email')

    if not usuario_id or usuario_tipo != 'administrador':
        return redirect('/login')

    return render_template('administrador.html', email=usuario_email)


@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco = request.form['preco'].replace('.', '').replace(',', '.')
        estoque = request.form['estoque']
        sem_validade = 'sem_validade' in request.form
        data_validade = None if sem_validade else request.form['validade']
        imagem = request.form['imagem']

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


@app.route('/consultar_produto', methods=['GET'])
def consultar_produto():
    filtro = request.args.get('filtro')

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    if filtro == "comentados":
        consulta = """
            SELECT p.* FROM produtos p
            WHERE EXISTS (
                SELECT 1 FROM comentarios_adm c
                WHERE c.produto_id = p.id
            )
            ORDER BY p.id DESC
        """
        cursor.execute(consulta)
    else:
        cursor.execute("SELECT * FROM produtos ORDER BY id DESC")

    produtos = cursor.fetchall()
    cursor.close()
    conexao.close()

    return render_template('consultar_produto.html', produtos=produtos)



@app.route('/excluir_produto/<int:id>', methods=['POST'])
def excluir_produto(id):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
        conexao.commit()

    except Exception as e:
        conexao.rollback()
        return "Ocorreu um erro ao excluir produto"
    finally:
        cursor.close()
        conexao.close()

    return redirect('/consultar_produto')



@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco = request.form['preco'].replace('.', '').replace(',', '.')
        sem_validade = 'sem_validade' in request.form
        data_validade = None if sem_validade else request.form['validade']
        estoque = request.form['estoque']
        imagem = request.form['imagem']

        try:
            sql = """
                UPDATE produtos 
                SET nome=%s, descricao=%s, categoria=%s, preco=%s, data_validade=%s, estoque=%s, sem_validade=%s, imagem=%s
                WHERE id=%s
            """
            valores = (nome, descricao, categoria, preco, data_validade, estoque, sem_validade, imagem, id)
            cursor.execute(sql, valores)
            conexao.commit()

            # <-- Aqui vem o redirecionamento
            return redirect('/consultar_produto')

        except Exception as e:
            conexao.rollback()
            flash(f'Erro ao atualizar produto: {e}', 'danger')

    # Se for GET, traz os dados para preencher o formulário
    cursor.execute("SELECT * FROM produtos WHERE id=%s", (id,))
    produto = cursor.fetchone()
    cursor.close()
    conexao.close()
    return render_template('editar_produto.html', produto=produto)



@app.route('/produto_detalhe/<int:produto_id>')
def produto_detalhe(produto_id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    # Buscar produto
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    if not produto:
        cursor.close()
        conexao.close()
        return "Produto não encontrado"

    # Buscar comentários
    cursor.execute("""
        SELECT c.*, u.nome AS usuario_nome
        FROM comentarios_adm c
        JOIN usuarios u ON u.id = c.usuario_id
        WHERE c.produto_id = %s
        ORDER BY c.data_criacao DESC
    """, (produto_id,))
    
    comentarios = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        'produto_detalhe.html',
        produto=produto,
        comentarios=comentarios
    )

    

@app.route('/produto_cliente/<int:produto_id>')
def produto_cliente(produto_id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    if produto:
        return render_template('produto_cliente.html', produto=produto)
    else:
        return "Produto não encontrado"



@app.route("/buscar_edicao", methods=["POST"])
def buscar_edicao():
    data = request.get_json()
    termo = data.get("termo", "").strip()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    if termo.isdigit():  # busca por ID
        cursor.execute("SELECT id FROM produtos WHERE id=%s", (termo,))
    else:  # busca por nome
        cursor.execute("SELECT id FROM produtos WHERE nome=%s", (termo,))
    
    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    if produto:
        return jsonify({"erro": False, "id": produto["id"]})
    else:
        return jsonify({"erro": True})



@app.route('/comentario_admin', methods=['POST'])
def comentario_admin():
    usuario_id = session.get('usuario_id')
    tipo_usuario = session.get('usuario_tipo')
    
    if not usuario_id or tipo_usuario != 'administrador':
        return jsonify({"erro": "Sem permissão"}), 403
    
    data = request.get_json()
    comentario = data.get('comentario', '').strip()
    produto_id = data.get('produto_id')
    parent_id = data.get('parent_id')

    if not comentario or not produto_id:
        return jsonify({"erro": "Dados incompletos"}), 400
    
    if not parent_id:
        parent_id = None

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            INSERT INTO comentarios_adm (usuario_id, produto_id, parent_id, comentario)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, produto_id, parent_id, comentario))

        conexao.commit()

        # pega o último ID inserido
        last_id = cursor.lastrowid

        # Buscar o nome do admin e a data de criação
        cursor.execute(""" SELECT c.comentario, c.data_criacao, c.parent_id, u.nome FROM comentarios_adm c JOIN usuarios u ON c.usuario_id = u.id WHERE c.id = %s """,(last_id,))

        novo_comentario = cursor.fetchone()

    except Exception as e:
        conexao.rollback()
        return jsonify({"erro": "Falha ao salvar comentário"}), 500
    
    finally:
        cursor.close()
        conexao.close()

    return jsonify(novo_comentario)





if __name__ == "__main__":
    app.run(debug=True)