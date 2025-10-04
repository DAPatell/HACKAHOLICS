from flask import Flask
from flask_jwt_extended import JWTManager
from models import db  # Import db from models
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize extensions
db.init_app(app)  # Bind db to app
jwt = JWTManager(app)

# Register blueprints
from routes_auth import *
from routes_manager import *
from routes_employee import *
from routes_admin import *
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(manager_bp, url_prefix='/manager')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)