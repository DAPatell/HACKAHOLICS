from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Expense, Approval, Company  # Import from models
from api_utils import convert_currency
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import re
from decimal import Decimal
from flask import current_app  # Use current_app for UPLOAD_FOLDER

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/submit_expense', methods=['POST'])
@jwt_required()
def submit_expense():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'employee':
        return jsonify({'msg': 'Access denied'}), 403
    data = request.get_json()
    amount = Decimal(data.get('amount'))
    currency = data.get('currency')
    category = data.get('category')
    description = data.get('description')
    date_str = data.get('date')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'msg': 'Invalid date format'}), 400
    expense = Expense(employee_id=user.id, amount=amount, currency=currency, category=category, description=description, date=date_obj)
    db.session.add(expense)
    db.session.commit()
    # Determine approval chain
    chain = []
    if user.is_manager_approver and user.manager_id:
        chain.append(user.manager_id)
    chain += user.company.approval_chain
    if chain:
        for seq, appr_id in enumerate(chain, 1):
            approval = Approval(expense_id=expense.id, approver_id=appr_id, sequence=seq)
            db.session.add(approval)
        db.session.commit()
    else:
        expense.status = 'approved'
        db.session.commit()
    return jsonify({'msg': 'Expense submitted', 'id': expense.id})

@employee_bp.route('/my_expenses', methods=['GET'])
@jwt_required()
def get_my_expenses():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'employee':
        return jsonify({'msg': 'Access denied'}), 403
    expenses = user.expenses
    result = []
    for e in expenses:
        result.append({
            'id': e.id,
            'amount': float(e.amount),
            'currency': e.currency,
            'category': e.category,
            'description': e.description,
            'date': str(e.date),
            'status': e.status
        })
    return jsonify(result)

@employee_bp.route('/submit_from_receipt', methods=['POST'])
@jwt_required()
def submit_from_receipt():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'employee':
        return jsonify({'msg': 'Access denied'}), 403
    if 'receipt' not in request.files:
        return jsonify({'msg': 'No receipt file'}), 400
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    # Perform OCR
    text = pytesseract.image_to_string(Image.open(filepath))
    # Simple parsing (improve with better regex or ML in production)
    amount_match = re.search(r'[\$€£]?(\d+(?:\.\d{2})?)', text)
    amount = Decimal(amount_match.group(1)) if amount_match else None
    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
    date_obj = None
    if date_match:
        date_str = date_match.group(1)
        try:
            if '/' in date_str:
                date_obj = datetime.strptime(date_str, '%m/%d/%Y').date()  # Adjust format as needed
            elif '-' in date_str:
                date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
        except ValueError:
            pass
    description = ''
    category = 'Other'
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        description = lines[0]  # Assume first line is vendor/description
        if 'restaurant' in text.lower() or 'food' in text.lower():
            category = 'Food'
        # Add more category logic as needed
    if amount is None:
        return jsonify({'msg': 'Could not extract amount from receipt'}), 400
    currency = user.company.currency  # Default to company currency
    date_obj = date_obj or datetime.today().date()
    expense = Expense(employee_id=user.id, amount=amount, currency=currency, category=category, description=description, date=date_obj)
    db.session.add(expense)
    db.session.commit()
    chain = []
    if user.is_manager_approver and user.manager_id:
        chain.append(user.manager_id)
    chain += user.company.approval_chain
    if chain:
        for seq, appr_id in enumerate(chain, 1):
            approval = Approval(expense_id=expense.id, approver_id=appr_id, sequence=seq)
            db.session.add(approval)
        db.session.commit()
    else:
        expense.status = 'approved'
        db.session.commit()
    return jsonify({'msg': 'Expense submitted from receipt', 'id': expense.id})