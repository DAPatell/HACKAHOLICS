"""
Email utility functions for password reset and notifications
"""
import secrets
import string
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from models import db, User, PasswordResetToken

# Initialize mail
mail = Mail()

def init_mail(app):
    """Initialize mail with Flask app"""
    mail.init_app(app)

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def send_password_reset_email(user_email, reset_token, reset_url):
    """Send password reset email to user"""
    try:
        msg = Message(
            subject='Password Reset Request - Expense Management System',
            recipients=[user_email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@expensemanager.com')
        )
        
        msg.html = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>You have requested to reset your password for the Expense Management System.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}?token={reset_token}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            <p>This link will expire in 1 hour for security reasons.</p>
            <p>If you did not request this password reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>Expense Management System Team</p>
        </body>
        </html>
        """
        
        msg.body = f"""
        Password Reset Request
        
        Hello,
        
        You have requested to reset your password for the Expense Management System.
        
        Click the link below to reset your password:
        {reset_url}?token={reset_token}
        
        This link will expire in 1 hour for security reasons.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        Expense Management System Team
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def create_password_reset_token(user_id):
    """Create a password reset token for user"""
    # Invalidate any existing tokens for this user
    PasswordResetToken.query.filter_by(user_id=user_id, used=False).update({'used': True})
    
    # Create new token
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.session.add(reset_token)
    db.session.commit()
    
    return token

def validate_reset_token(token):
    """Validate password reset token"""
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token:
        return None, "Invalid token"
    
    if not reset_token.is_valid():
        return None, "Token expired or already used"
    
    return reset_token, None

def mark_token_as_used(token):
    """Mark reset token as used"""
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    if reset_token:
        reset_token.used = True
        db.session.commit()
        return True
    return False

def send_notification_email(user_email, subject, message):
    """Send general notification email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@expensemanager.com')
        )
        
        msg.html = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <p>{message}</p>
            <br>
            <p>Best regards,<br>Expense Management System Team</p>
        </body>
        </html>
        """
        
        msg.body = f"{subject}\n\n{message}\n\nBest regards,\nExpense Management System Team"
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False
