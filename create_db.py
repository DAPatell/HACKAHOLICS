# create_db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import models
from models import Company, User, Expense, ApprovalStep, ApprovalRule

# Create database and tables
with app.app_context():
    db.create_all()
    print("Database created successfully!")