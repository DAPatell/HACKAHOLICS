from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Expense, Approval, Company  # Import from models
from api_utils import convert_currency

manager_bp = Blueprint('manager', __name__)


def handle_approval(expense, approval, new_status, comments):
    approval.status = new_status
    approval.comments = comments
    db.session.commit()
    # Check if all approvals have been acted upon
    all_approvals = expense.approval_steps
    if all(a.status != 'pending' for a in all_approvals):
        # Evaluate the approval rule
        approved_count = sum(1 for a in all_approvals if a.status == 'approved')
        total = len(all_approvals)
        company = expense.employee.company
        rule_type = company.approval_rule_type
        is_approved = False
        if rule_type == 'all':
            is_approved = approved_count == total
        elif rule_type == 'percentage':
            is_approved = (approved_count / total) >= (company.percentage / 100) if company.percentage else False
        elif rule_type == 'specific':
            is_approved = any(a.status == 'approved' and a.approver_id == company.specific_approver_id for a in all_approvals)
        elif rule_type == 'hybrid':
            percentage_met = (approved_count / total) >= (company.percentage / 100) if company.percentage else False
            specific_met = any(a.status == 'approved' and a.approver_id == company.specific_approver_id for a in all_approvals)
            is_approved = percentage_met or specific_met
        expense.status = 'approved' if is_approved else 'rejected'
        db.session.commit()

@manager_bp.route('/pending_expenses', methods=['GET'])
@jwt_required()
def get_pending_expenses():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    # Find pending approvals where previous sequences have been completed
    pending_approvals = []
    for approval in Approval.query.filter_by(approver_id=current_user_id, status='pending').all():
        expense = approval.expense
        previous_approvals = Approval.query.filter_by(expense_id=expense.id).filter(Approval.sequence < approval.sequence).all()
        if all(a.status != 'pending' for a in previous_approvals):
            pending_approvals.append(approval)
    result = []
    for pa in pending_approvals:
        e = pa.expense
        amount_company = convert_currency(e.amount, e.currency, user.company.currency)
        result.append({
            'id': e.id,
            'approval_id': pa.id,
            'employee': e.employee.username,
            'amount': float(amount_company),
            'currency': user.company.currency,
            'category': e.category,
            'description': e.description,
            'date': str(e.date),
            'sequence': pa.sequence
        })
    return jsonify(result)

@manager_bp.route('/approve/<int:approval_id>', methods=['POST'])
@jwt_required()
def approve(approval_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    approval = Approval.query.get(approval_id)
    if not approval or approval.approver_id != current_user_id or approval.status != 'pending':
        return jsonify({'msg': 'Invalid approval'}), 404
    # Ensure previous approvals are completed
    previous = Approval.query.filter_by(expense_id=approval.expense_id).filter(Approval.sequence < approval.sequence).all()
    if not all(a.status != 'pending' for a in previous):
        return jsonify({'msg': 'Previous approvals not completed'}), 403
    data = request.get_json()
    comments = data.get('comments', '')
    handle_approval(approval.expense, approval, 'approved', comments)
    return jsonify({'msg': 'Approved'})

@manager_bp.route('/reject/<int:approval_id>', methods=['POST'])
@jwt_required()
def reject(approval_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    approval = Approval.query.get(approval_id)
    if not approval or approval.approver_id != current_user_id or approval.status != 'pending':
        return jsonify({'msg': 'Invalid approval'}), 404
    # Ensure previous approvals are completed
    previous = Approval.query.filter_by(expense_id=approval.expense_id).filter(Approval.sequence < approval.sequence).all()
    if not all(a.status != 'pending' for a in previous):
        return jsonify({'msg': 'Previous approvals not completed'}), 403
    data = request.get_json()
    comments = data.get('comments', '')
    handle_approval(approval.expense, approval, 'rejected', comments)
    return jsonify({'msg': 'Rejected'})

@manager_bp.route('/team_expenses', methods=['GET'])
@jwt_required()
def get_team_expenses():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user.role != 'manager':
        return jsonify({'msg': 'Access denied'}), 403
    # Get expenses from direct reports
    team_expenses = Expense.query.filter(Expense.employee_id.in_([e.id for e in user.employees])).all()
    result = []
    for e in team_expenses:
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