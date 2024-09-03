# test_flask_login.py
try:
    from flask_login import LoginManager
    print("Flask-Login importado com sucesso!")
except ModuleNotFoundError:
    print("Erro: Flask-Login não está instalado.")
