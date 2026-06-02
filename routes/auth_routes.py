from flask import Blueprint
from controllers.auth_controller import signup, login

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_bp.post("/signup")(signup)
auth_bp.post("/login")(login)
