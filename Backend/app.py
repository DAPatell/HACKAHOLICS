from flask import Flask
from flask_jwt_extended import JWTManager
from models import db  # Import db from models
from email_utils import init_mail
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change to your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@expensemanager.com')
app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Initialize extensions
db.init_app(app)  # Bind db to app
jwt = JWTManager(app)
init_mail(app)  # Initialize email

# Register blueprints
from routes_auth import *
from routes_manager import *
from routes_employee import *
from routes_admin import *
from routes_password_reset import *
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(manager_bp, url_prefix='/manager')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(password_reset_bp, url_prefix='/password')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)