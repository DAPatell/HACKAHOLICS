from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Expense, Approval

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    
    expenses = Expense.query.join(User).filter(User.manager_id == current_user_id).all()
    result = []
    for e in expenses:
        result.append({
            'id': e.id,
            'employee': e.employee.username,
            'amount': e.amount,
            'currency': e.currency,
            'category': e.category,
            'description': e.description,
            'date': str(e.date),
            'status': e.status
        })
    return jsonify(result)

@manager_bp.route('/approve/<int:expense_id>', methods=['POST'])
@jwt_required()
def approve_expense(expense_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    
    expense = Expense.query.get(expense_id)
    if not expense or expense.employee.manager_id != current_user_id:
        return jsonify({'msg': 'Expense not found'}), 404
    
    data = request.get_json()
    status = data.get('status')
    comments = data.get('comments', '')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'msg': 'Invalid status'}), 400
    
    expense.status = status
    db.session.commit()
    
    return jsonify({'msg': f'Expense {status}'})