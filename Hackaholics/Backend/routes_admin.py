from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Expense, Company, Approval  # Import from models
from werkzeug.security import generate_password_hash
from api_utils import convert_currency

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/create_user', methods=['POST'])
@jwt_required()
def create_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    manager_id = data.get('manager_id')
    is_manager_approver = data.get('is_manager_approver', True)
    if not all([username, email, password, role]):
        return jsonify({'msg': 'Missing fields'}), 400
    if role not in ['employee', 'manager']:
        return jsonify({'msg': 'Invalid role'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already exists'}), 400
    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash, role=role, company_id=user.company_id, manager_id=manager_id, is_manager_approver=is_manager_approver)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg': 'User created', 'id': new_user.id})

@admin_bp.route('/update_user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    target_user = User.query.get(user_id)
    if not target_user or target_user.company_id != user.company_id:
        return jsonify({'msg': 'User not found'}), 404
    data = request.get_json()
    if 'role' in data and data['role'] in ['employee', 'manager']:
        target_user.role = data['role']
    if 'manager_id' in data:
        target_user.manager_id = data['manager_id']
    if 'is_manager_approver' in data:
        target_user.is_manager_approver = data['is_manager_approver']
    db.session.commit()
    return jsonify({'msg': 'User updated'})

@admin_bp.route('/set_approval_rules', methods=['POST'])
@jwt_required()
def set_approval_rules():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    company = user.company
    if 'rule_type' in data and data['rule_type'] in ['all', 'percentage', 'specific', 'hybrid']:
        company.approval_rule_type = data['rule_type']
    if 'percentage' in data:
        company.percentage = data['percentage']
    if 'specific_approver_id' in data:
        company.specific_approver_id = data['specific_approver_id']
    if 'approval_chain' in data and isinstance(data['approval_chain'], list):
        company.approval_chain = data['approval_chain']
    db.session.commit()
    return jsonify({'msg': 'Approval rules updated'})

@admin_bp.route('/all_expenses', methods=['GET'])
@jwt_required()
def get_all_expenses():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    expenses = Expense.query.join(User).filter(User.company_id == user.company_id).all()
    result = []
    for e in expenses:
        amount_company = convert_currency(e.amount, e.currency, user.company.currency)
        result.append({
            'id': e.id,
            'employee': e.employee.username,
            'amount': float(amount_company),
            'currency': user.company.currency,
            'category': e.category,
            'description': e.description,
            'date': str(e.date),
            'status': e.status
        })
    return jsonify(result)

@admin_bp.route('/override_expense/<int:expense_id>', methods=['POST'])
@jwt_required()
def override_expense(expense_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'admin':
        return jsonify({'msg': 'Access denied'}), 403
    expense = Expense.query.get(expense_id)
    if not expense or expense.employee.company_id != user.company_id:
        return jsonify({'msg': 'Expense not found'}), 404
    data = request.get_json()
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({'msg': 'Invalid status'}), 400
    expense.status = status
    db.session.commit()
    return jsonify({'msg': 'Expense status overridden'})