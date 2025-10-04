from flask import Blueprint, jsonify, request
from models import db, User
from email_utils import mail
from flask_mail import Message

password_reset_bp = Blueprint('password_reset', __name__)

@password_reset_bp.route('/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'msg': 'Email required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    # In production, generate a secure token
    reset_token = "temp_token_123"
    
    msg = Message(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click here to reset your password: {reset_token}"
    )
    
    try:
        mail.send(msg)
        return jsonify({'msg': 'Password reset email sent'})
    except Exception as e:
        return jsonify({'msg': 'Failed to send email'}), 500

@password_reset_bp.route('/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    
    if not all([token, new_password]):
        return jsonify({'msg': 'Token and password required'}), 400
    
    # In production, verify the token
    if token != "temp_token_123":
        return jsonify({'msg': 'Invalid token'}), 400
    
    # Find user by token (in production, store token in database)
    user = User.query.first()  # Simplified for demo
    
    if user:
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'msg': 'Password reset successful'})
    
    return jsonify({'msg': 'User not found'}), 404