"""
Password reset routes and functionality
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User
from email_utils import (
    create_password_reset_token, 
    send_password_reset_email, 
    validate_reset_token, 
    mark_token_as_used
)

password_reset_bp = Blueprint('password_reset', __name__)

@password_reset_bp.route('/request_reset', methods=['POST'])
def request_password_reset():
    """Request password reset for user"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'msg': 'Email is required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Don't reveal if email exists or not for security
        return jsonify({'msg': 'If the email exists, a password reset link has been sent'}), 200
    
    # Create reset token
    token = create_password_reset_token(user.id)
    
    # Generate reset URL
    reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password"
    
    # Send email
    email_sent = send_password_reset_email(user.email, token, reset_url)
    
    if email_sent:
        return jsonify({'msg': 'Password reset link has been sent to your email'}), 200
    else:
        return jsonify({'msg': 'Failed to send reset email. Please try again.'}), 500

@password_reset_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not all([token, new_password]):
        return jsonify({'msg': 'Token and new password are required'}), 400
    
    # Validate token
    reset_token, error = validate_reset_token(token)
    
    if error:
        return jsonify({'msg': error}), 400
    
    # Update user password
    user = reset_token.user
    user.password = new_password
    user.password_hash = generate_password_hash(new_password)
    
    # Mark token as used
    mark_token_as_used(token)
    
    db.session.commit()
    
    return jsonify({'msg': 'Password has been reset successfully'}), 200

@password_reset_bp.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not all([current_password, new_password]):
        return jsonify({'msg': 'Current password and new password are required'}), 400
    
    # Verify current password
    from werkzeug.security import check_password_hash
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'msg': 'Current password is incorrect'}), 400
    
    # Update password
    user.password = new_password
    user.password_hash = generate_password_hash(new_password)
    
    db.session.commit()
    
    return jsonify({'msg': 'Password changed successfully'}), 200

@password_reset_bp.route('/validate_token', methods=['POST'])
def validate_token():
    """Validate password reset token"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'msg': 'Token is required'}), 400
    
    reset_token, error = validate_reset_token(token)
    
    if error:
        return jsonify({'msg': error}), 400
    
    return jsonify({'msg': 'Token is valid', 'user_id': reset_token.user_id}), 200
