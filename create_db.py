# create_db.py
from app import app, db
from models import Company, User, Expense, ApprovalRule, Approval

# Create database and tables
with app.app_context():
    db.create_all()
    print("Database created successfully!")