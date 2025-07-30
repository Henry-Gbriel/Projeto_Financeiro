from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from config import POSTGRES_CONFIG
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message
import psycopg2
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = secrets.token_hex(32)

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'henryautomationprojects@gmail.com'
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)

# Função para conectar ao PostgreSQL

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_CONFIG['host'],
        port=POSTGRES_CONFIG['port'],
        user=POSTGRES_CONFIG['user'],
        password=POSTGRES_CONFIG['password'],
        dbname=POSTGRES_CONFIG['database']
    )

# Rotas frontend
@app.route('/')
def criacao_page():
    return render_template('criacao.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/esqui')
def esqueci_page():
    return render_template('esqui.html')

@app.route('/intro')
def intro_page():
    return render_template('intro.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/historico')
def historico_page():
    return render_template('his.html')

@app.route('/envio')
def envio_page():
    return render_template('envio.html')

# API: Criar Acesso
@app.route('/api/criar-acesso', methods=['POST'])
def criar_acesso():
    try:
        dados = request.get_json() or request.form
        nome = dados['nome']
        email = dados['email']
        cargo = dados['cargo']
        senha = generate_password_hash(dados['senha'])

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({'erro': 'E-mail já cadastrado!'}), 400

        cur.execute("INSERT INTO usuarios (nome, email, cargo, senha) VALUES (%s, %s, %s, %s)",
                    (nome, email, cargo, senha))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensagem': 'Usuário criado com sucesso!'}), 200
    except Exception as e:
        print("❌ ERRO AO CRIAR ACESSO:", e)
        return jsonify({'erro': 'Erro interno ao criar usuário.'}), 500

# API: Login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')

        if not email or not senha:
            return jsonify({'erro': 'E-mail e senha são obrigatórios.'}), 400

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email, cargo, senha FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if usuario:
            senha_criptografada = usuario[4]
            if check_password_hash(senha_criptografada, senha):
                session['usuario_id'] = usuario[0]
                session['usuario_nome'] = usuario[1]
                return jsonify({'mensagem': 'Login realizado com sucesso!'}), 200
            else:
                return jsonify({'erro': 'Senha incorreta.'}), 401
        else:
            return jsonify({'erro': 'E-mail não encontrado.'}), 401
    except Exception as e:
        print("❌ ERRO NO LOGIN:", e)
        return jsonify({'erro': 'Erro interno no login'}), 500

# Função para enviar e-mail
EMAIL_ADDRESS = 'henryautomationprojects@gmail.com'
EMAIL_PASSWORD = 'ncyv ubzi rgaj omps'

def enviar_email(destinatario, senha_temporaria):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = destinatario
    msg['Subject'] = 'Recuperação de senha - Sua nova senha'
    corpo = f"""
    Olá,

    Você solicitou a recuperação de senha.
    Sua nova senha é: {senha_temporaria}

    Por favor, use esta senha para acessar sua conta e altere-a assim que possível.

    Caso não tenha solicitado, ignore este e-mail.

    Atenciosamente,
    Sua equipe
    """
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print('Erro ao enviar email:', e)
        return False

# API: Esqueci Senha
@app.route('/api/esqueci-senha', methods=['POST'])
def esqueci_senha():
    dados = request.get_json()
    email = dados.get('email')

    if not email:
        return jsonify({'erro': 'E-mail é obrigatório'}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()

    if not usuario:
        cur.close()
        conn.close()
        return jsonify({'erro': 'E-mail não cadastrado'}), 404

    senha_temporaria = secrets.token_urlsafe(8)
    senha_hash = generate_password_hash(senha_temporaria)

    cur.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (senha_hash, usuario[0]))
    conn.commit()
    cur.close()
    conn.close()

    sucesso = enviar_email(email, senha_temporaria)
    if sucesso:
        return jsonify({'mensagem': 'Sua nova senha foi enviada para o seu e-mail.'}), 200
    else:
        return jsonify({'erro': 'Erro ao enviar o e-mail. Tente novamente mais tarde.'}), 500

# API: Obter nome do colaborador
@app.route("/api/colaborador")
def get_colaborador():
    nome = session.get('usuario_nome')
    usuario_id = session.get('usuario_id')

    if not nome or not usuario_id:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT email FROM usuarios WHERE id = %s", (usuario_id,))
        email = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"nome": nome, "email": email})
    except Exception as e:
        print("Erro ao buscar colaborador:", e)
        return jsonify({"erro": "Erro interno"}), 500

# API: Reportar erro
@app.route("/api/chamado", methods=["POST"])
def chamado_erro():
    data = request.get_json()
    nome = data.get("nome", "Desconhecido")
    email_colaborador = data.get("email", "email desconhecido")

    try:
        corpo_email = f"""
        O colaborador {nome} ({email_colaborador}) encontrou um erro no sistema.
        """

        msg = Message(
            subject="🚨 Erro reportado no sistema",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],  # envia para você mesmo
            body=corpo_email
        )
        mail.send(msg)
        return jsonify({"status": "ok", "mensagem": "Chamado enviado com sucesso!"})
    except Exception as e:
        print("Erro ao enviar chamado:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
