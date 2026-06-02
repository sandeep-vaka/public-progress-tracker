from flask import request, jsonify
from datetime import datetime, timezone
from models.progress import Progress


def create_progress(current_user):
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    progress = Progress(
        title=title,
        description=data.get("description", ""),
        progress_status=data.get("progress_status", "not_started"),
        created_by=current_user,
    ).save()

    return jsonify({"message": "Progress created", "progress": progress.to_dict()}), 201


def get_my_progress(current_user):
    items = Progress.objects(created_by=current_user)
    return jsonify([p.to_dict() for p in items]), 200


def update_progress(current_user, progress_id):
    progress = Progress.objects(id=progress_id, created_by=current_user).first()
    if not progress:
        return jsonify({"error": "Not found or unauthorized"}), 404

    data = request.get_json()
    progress.title = data.get("title", progress.title)
    progress.description = data.get("description", progress.description)
    progress.progress_status = data.get("progress_status", progress.progress_status)
    progress.updated_at = datetime.now(timezone.utc)
    progress.save()

    return jsonify({"message": "Updated", "progress": progress.to_dict()}), 200


def delete_progress(current_user, progress_id):
    progress = Progress.objects(id=progress_id, created_by=current_user).first()
    if not progress:
        return jsonify({"error": "Not found or unauthorized"}), 404

    progress.delete()
    return jsonify({"message": "Deleted"}), 200


# Public endpoint — no auth
def get_all_progress():
    items = Progress.objects().order_by("-created_at")
    return jsonify([p.to_dict() for p in items]), 200
