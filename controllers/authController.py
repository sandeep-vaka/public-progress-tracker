import os
from flask import request, jsonify
from utils.jwtHelper import generate_token

def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400
    if username == os.getenv("ADMIN_USERNAME", "") and \
       password == os.getenv("ADMIN_PASSWORD", ""):
        return jsonify({"token": generate_token(username)}), 200
    return jsonify({"message": "Invalid credentials"}), 401