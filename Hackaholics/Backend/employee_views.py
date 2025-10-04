# employee_views.py
from app import app, db
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from api_utils import convert_currency

def is_employee(user_id):
    from models import User
    user = User.query.get(user_id)
    return user and user.role == 'Employee'

@app.route('/expenses/submit', methods=['POST'])
@jwt_required()
def submit_expense():
    user_id = get_jwt_identity()
    if not is_employee(user_id):
        return jsonify({"msg": "Employee access required"}), 403
    data = request.json
    from models import Expense, User
    user = User.query.get(user_id)
    submitted_currency = data.get('currency', user.company.currency)
    amount = data.get('amount')
    if submitted_currency != user.company.currency:
        amount = convert_currency(amount, submitted_currency, user.company.currency)
    expense = Expense(
        employee_id=user_id,
        amount=amount,
        currency=user.company.currency,
        category=data.get('category'),
        description=data.get('description'),
        date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else datetime.today().date()
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({"msg": "Expense submitted", "expense_id": expense.id}), 201