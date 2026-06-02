from functools import wraps
from flask import request, jsonify
from utils.jwtHelper import verify_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Authorization header missing or malformed"}), 401
        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return jsonify({"message": "Bearer token is empty"}), 401
        decoded = verify_token(token)
        if decoded is None:
            return jsonify({"message": "Invalid or expired token"}), 401
        request.user = decoded
        return f(*args, **kwargs)
    return decorated