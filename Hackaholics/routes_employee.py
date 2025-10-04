from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Expense

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_my_expenses():
    current_user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(employee_id=current_user_id).all()
    result = []
    for e in expenses:
        result.append({
            'id': e.id,
            'amount': e.amount,
            'currency': e.currency,
            'category': e.category,
            'description': e.description,
            'date': str(e.date),
            'status': e.status
        })
    return jsonify(result)

@employee_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    amount = data.get('amount')
    currency = data.get('currency')
    category = data.get('category')
    description = data.get('description')
    
    if not all([amount, currency, category]):
        return jsonify({'msg': 'Missing required fields'}), 400
    
    expense = Expense(
        employee_id=current_user_id,
        amount=amount,
        currency=currency,
        category=category,
        description=description
    )
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify({'msg': 'Expense created', 'id': expense.id})