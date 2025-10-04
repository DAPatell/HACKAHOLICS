# models.py
from app import db
from datetime import date

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    is_manager_approver = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Company {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # In production, hash this
    role = db.Column(db.String(20), nullable=False)  # 'Admin', 'Manager', 'Employee'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    company = db.relationship('Company', backref=db.backref('users', lazy=True))
    manager = db.relationship('User', remote_side=[id], backref=db.backref('subordinates', lazy=True))

    def __repr__(self):
        return f'<User {self.username}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'

    employee = db.relationship('User', backref=db.backref('expenses', lazy=True))

    def __repr__(self):
        return f'<Expense {self.id} by {self.employee.username}>'

class ApprovalStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    comments = db.Column(db.Text)

    expense = db.relationship('Expense', backref=db.backref('approval_steps', lazy=True))
    approver = db.relationship('User', backref=db.backref('approvals', lazy=True))

    def __repr__(self):
        return f'<ApprovalStep {self.id} for Expense {self.expense_id}>'

class ApprovalRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    rule_type = db.Column(db.String(20), nullable=False)  # 'percentage', 'specific', 'hybrid'
    details = db.Column(db.JSON, nullable=False)  # e.g., {'percentage': 60, 'specific_approver_id': 1, 'approvers': [1,2,3], 'sequential': True}

    company = db.relationship('Company', backref=db.backref('approval_rules', lazy=True))

    def __repr__(self):
        return f'<ApprovalRule {self.id} for Company {self.company_id}>'