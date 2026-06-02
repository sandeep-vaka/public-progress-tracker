from flask import Blueprint
from controllers.authController import login

auth_bp = Blueprint("auth", __name__)
auth_bp.add_url_rule("/login", "login", login, methods=["POST"])