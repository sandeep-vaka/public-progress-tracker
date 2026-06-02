from flask import Blueprint
from middlewares.authMiddleware import token_required
from controllers.trackerController import (
    add_update, edit_update, delete_update, toggle_pin,
    get_updates, get_stats, get_meta,
)

tracker_bp = Blueprint("tracker", __name__)

# Public
tracker_bp.add_url_rule("/updates",          "get_updates", get_updates,               methods=["GET"])
tracker_bp.add_url_rule("/stats",            "get_stats",   get_stats,                 methods=["GET"])
tracker_bp.add_url_rule("/meta",             "get_meta",    get_meta,                  methods=["GET"])

# Protected
tracker_bp.add_url_rule("/updates",          "add_update",  token_required(add_update),    methods=["POST"])
tracker_bp.add_url_rule("/updates/<id>",     "edit_update", token_required(edit_update),   methods=["PUT"])
tracker_bp.add_url_rule("/updates/<id>",     "del_update",  token_required(delete_update), methods=["DELETE"])
tracker_bp.add_url_rule("/updates/<id>/pin", "toggle_pin",  token_required(toggle_pin),    methods=["PUT"])