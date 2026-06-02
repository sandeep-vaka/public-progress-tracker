from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from config.settings import Config
import jwt
from datetime import datetime, timedelta, timezone


def signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.objects(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    user = User(name=name, email=email, password=hashed).save()

    return jsonify({"message": "User created", "user": user.to_dict()}), 201


def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.objects(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "user_id": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token, "user": user.to_dict()}), 200
