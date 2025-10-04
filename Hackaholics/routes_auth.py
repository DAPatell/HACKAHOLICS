from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User, Company  # Import from models
from api_utils import get_country_currency

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    country = data.get('country')
    if not all([username, email, password, country]):
        return jsonify({'msg': 'Missing fields'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already exists'}), 400
    currency = get_country_currency(country)
    company = Company(name=f"{username}'s Company", currency=currency)
    db.session.add(company)
    db.session.commit()
    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password=password, password_hash=password_hash, role='admin', company_id=company.id)
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token})
    return jsonify({'msg': 'Invalid credentials'}), 401