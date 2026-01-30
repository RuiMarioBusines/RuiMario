from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

app = Flask(__name__)
app.secret_key = 'mauro_secret_key_123'

# Configuração de Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Banco de Dados Temporário (Dicionários)
users = {} # {email: {'password': pwd, 'name': name}}
agendamentos = []

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# --- Lógica de Localização ---
def get_user_location(ip):
    try:
        # Em localhost o IP é 127.0.0.1, a API não localiza. 
        # Forçamos um IP de Luanda/PT para teste se for local.
        target_ip = ip if ip != '127.0.0.1' else '' 
        response = requests.get(f'http://ip-api.com/json/{target_ip}').json()
        return f"{response.get('city', 'Desconhecida')}, {response.get('country', 'Mauro Business')}"
    except:
        return "Localização Indisponível"

# --- Template HTML Único (CSS e JS inclusos) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mauro Business - Premium</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background-color: #1a1a1a; }
        .hero { background: linear-gradient(45deg, #1a1a1a, #333); color: white; padding: 60px 0; }
        .card { border: none; transition: 0.3s; }
        .card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">MAURO BUSINESS 📱</a>
            <div class="navbar-nav ms-auto">
                {% if current_user.is_authenticated %}
                    <span class="nav-link text-light">Olá, {{ current_user.id }}</span>
                    <a class="nav-link" href="/agendar">Agendar</a>
                    <a class="nav-link btn btn-outline-danger btn-sm ms-2" href="/logout">Sair</a>
                {% else %}
                    <a class="nav-link" href="/login">Login</a>
                    <a class="nav-link" href="/signup">Cadastrar</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="alert alert-info py-2">
            📍 <strong>Sua Localização:</strong> {{ localizacao }}
        </div>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-warning alert-dismissible fade show">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {% block content %}
        <div class="hero text-center rounded-3 mb-5">
            <h1>Telefonia & Acessórios</h1>
            <p>O melhor de Angola e do mundo na Mauro Business.</p>
        </div>
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm p-3">
                    <h5>iPhone 15 Pro</h5>
                    <p class="text-success fw-bold">R$ 7.500</p>
                    <button class="btn btn-dark" onclick="alertaCompra()">Comprar Agora</button>
                </div>
            </div>
            </div>
        {% endblock %}
    </div>

    <script>
        function alertaCompra() {
            alert("Produto adicionado ao carrinho! Mauro Business agradece.");
        }
    </script>
</body>
</html>
"""

# --- Rotas ---

@app.route('/')
def index():
    loc = get_user_location(request.remote_addr)
    return render_template_string(HTML_TEMPLATE, localizacao=loc)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in users:
            flash("E-mail já cadastrado!")
        else:
            users[email] = {'password': request.form.get('password')}
            flash("Cadastro realizado! Faça login.")
            return redirect(url_for('login'))
    
    content = """
    <div class="row justify-content-center">
        <div class="col-md-4 card p-4 shadow">
            <h3>Criar Conta</h3>
            <form method="POST">
                <input type="email" name="email" class="form-control mb-2" placeholder="Seu E-mail" required>
                <input type="password" name="password" class="form-control mb-3" placeholder="Senha" required>
                <button type="submit" class="btn btn-primary w-100">Registrar</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=content, localizacao="Mauro Business Store")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in users and users[email]['password'] == password:
            user = User(email)
            login_user(user)
            return redirect(url_for('index'))
        flash("Credenciais inválidas!")
    
    content = """
    <div class="row justify-content-center">
        <div class="col-md-4 card p-4 shadow">
            <h3>Login - Mauro Business</h3>
            <form method="POST">
                <input type="email" name="email" class="form-control mb-2" placeholder="E-mail" required>
                <input type="password" name="password" class="form-control mb-3" placeholder="Senha" required>
                <button type="submit" class="btn btn-dark w-100">Entrar</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=content, localizacao="Área de Acesso")

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        servico = request.form.get('servico')
        data = request.form.get('data')
        agendamentos.append({'user': current_user.id, 'servico': servico, 'data': data})
        flash(f"Agendamento de {servico} confirmado para {data}!")
        return redirect(url_for('index'))

    content = """
    <div class="row justify-content-center">
        <div class="col-md-6 card p-4 shadow">
            <h3>Agendar Assistência Técnica</h3>
            <form method="POST">
                <label>Serviço:</label>
                <select name="servico" class="form-control mb-2">
                    <option>Troca de Tela</option>
                    <option>Troca de Bateria</option>
                    <option>Configuração de Software</option>
                </select>
                <label>Data:</label>
                <input type="date" name="data" class="form-control mb-3" required>
                <button type="submit" class="btn btn-success w-100">Confirmar Agendamento</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(HTML_TEMPLATE, content=content, localizacao="Setor de Agendamentos")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
