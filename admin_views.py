# admin_views.py
from app import app, db
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import requests

def is_admin(user_id):
    from models import User
    user = User.query.get(user_id)
    return user and user.role == 'Admin'

@app.route('/signup', methods=['POST'])
def signup():
    from models import Company, User
    data = request.json
    username = data.get('username')
    password = data.get('password')
    country = data.get('country', 'United States')
    try:
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,currencies')
        response.raise_for_status()
        countries_data = response.json()
        currency = 'USD'
        for country_data in countries_data:
            if country_data['name']['common'] == country or country_data['name']['official'] == country:
                currencies = country_data.get('currencies', {})
                currency = list(currencies.keys())[0] if currencies else 'USD'
                break
    except requests.RequestException:
        currency = 'USD'
    company = Company(name=f"{username}'s Company", currency=currency)
    db.session.add(company)
    db.session.commit()
    admin = User(username=username, password=password, role='Admin', company_id=company.id)
    db.session.add(admin)
    db.session.commit()
    access_token = create_access_token(identity=admin.id)
    return jsonify(access_token=access_token), 201

@app.route('/login', methods=['POST'])
def login():
    from models import User
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.password == data.get('password'):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    from models import User
    current_user_id = get_jwt_identity()
    if not is_admin(current_user_id):
        return jsonify({"msg": "Admin access required"}), 403
    data = request.json
    company_id = User.query.get(current_user_id).company_id
    new_user = User(
        username=data.get('username'),
        password=data.get('password'),
        role=data.get('role'),
        company_id=company_id,
        manager_id=data.get('manager_id')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created", "user_id": new_user.id}), 201