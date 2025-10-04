from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_jwt_extended import JWTManager
from models import db
from email_utils import init_mail
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@expensemanager.com')
app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5000')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
init_mail(app)

# Register blueprints
from routes_auth import auth_bp
from routes_manager import manager_bp
from routes_employee import employee_bp
from routes_admin import admin_bp
from routes_password_reset import password_reset_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(manager_bp, url_prefix='/manager')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(password_reset_bp, url_prefix='/password')

# Frontend routes
@app.route('/')
def index():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login_frontend():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Call the auth API
    import requests
    response = requests.post('http://localhost:5000/auth/login', 
                           json={'email': email, 'password': password})
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        session['token'] = token
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
