from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, login_user, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chamados.db'
app.config['SECURITY_PASSWORD_SALT'] = 'salt_secreto'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chamados', lazy=True))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = user_datastore.hash_password(password)
        user_datastore.create_user(username=username, password=hashed_password)
        db.session.commit()
        flash('Usuário registrado com sucesso! Faça login para continuar.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_datastore.find_user(username=username)
        if user and user_datastore.verify_password(password, user):
            login_user(user)
            return redirect(url_for('home'))
        flash('Nome de usuário ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/criar_chamado', methods=['GET', 'POST'])
@login_required
def criar_chamado():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        novo_chamado = Chamado(titulo=titulo, descricao=descricao, user_id=current_user.id)
        db.session.add(novo_chamado)
        db.session.commit()
        return redirect(url_for('ver_chamados'))
    return render_template('criar_chamado.html')

@app.route('/ver_chamados')
@login_required
def ver_chamados():
    chamados = Chamado.query.filter_by(user_id=current_user.id).all()
    return render_template('ver_chamados.html', chamados=chamados)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criar o banco de dados e as tabelas
    app.run(debug=True)
