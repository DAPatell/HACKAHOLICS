# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-in-production'

db = SQLAlchemy(app)
jwt = JWTManager(app)

from models import *
from admin_views import *
from employee_views import *

if __name__ == '__main__':
    app.run(debug=True)