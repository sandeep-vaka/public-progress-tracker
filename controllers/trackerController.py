import os
from datetime import datetime, date, timedelta

from bson import ObjectId
from bson.errors import InvalidId
from flask import request, jsonify
from pymongo import DESCENDING, ReturnDocument

from config import db


# ── Constants ───────────────────────────────────────────────────────────────
VALID_STATUSES   = ["planned", "in-progress", "done", "blocked"]
VALID_CATEGORIES = ["backend", "frontend", "database", "auth", "deployment", "other"]


# ── Private helpers ──────────────────────────────────────────────────────────

def _serialize(doc: dict) -> dict:
    """Convert ObjectId and datetime fields to JSON-safe types in-place."""
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()
    return doc


def _parse_object_id(id_str: str):
    """Parse a string into ObjectId; return None on any error."""
    try:
        return ObjectId(id_str)
    except (InvalidId, Exception):
        return None


# ── Protected endpoints (JWT required) ──────────────────────────────────────

def add_update():
    """
    POST /updates
    Body: { title, description?, status?, category?, pinned? }
    Returns the created document.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify({"message": "title is required"}), 400

    status   = data.get("status",   "planned")
    category = data.get("category", "other")

    if status not in VALID_STATUSES:
        return jsonify({
            "message": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
        }), 400

    if category not in VALID_CATEGORIES:
        return jsonify({
            "message": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
        }), 400

    now = datetime.utcnow()
    doc = {
        "title":       title,
        "description": str(data.get("description", "")).strip(),
        "status":      status,
        "category":    category,
        "pinned":      bool(data.get("pinned", False)),
        "created_at":  now,
        "updated_at":  now,
    }

    result = db.updates.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["created_at"] = doc["created_at"].isoformat()
    doc["updated_at"] = doc["updated_at"].isoformat()

    return jsonify({"message": "Update added successfully", "update": doc}), 201


def edit_update(id):
    """
    PUT /updates/<id>
    Body: any subset of { title, description, status, category, pinned }
    Returns the updated document.
    """
    obj_id = _parse_object_id(id)
    if obj_id is None:
        return jsonify({"message": "Invalid update ID"}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Request body must be JSON"}), 400

    fields = {}

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return jsonify({"message": "title cannot be empty"}), 400
        fields["title"] = title

    if "description" in data:
        fields["description"] = str(data["description"]).strip()

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({
                "message": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            }), 400
        fields["status"] = data["status"]

    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return jsonify({
                "message": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
            }), 400
        fields["category"] = data["category"]

    if "pinned" in data:
        fields["pinned"] = bool(data["pinned"])

    if not fields:
        return jsonify({"message": "No valid fields to update"}), 400

    fields["updated_at"] = datetime.utcnow()

    updated = db.updates.find_one_and_update(
        {"_id": obj_id},
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )

    if updated is None:
        return jsonify({"message": "Update not found"}), 404

    return jsonify({
        "message": "Update edited successfully",
        "update": _serialize(updated),
    }), 200


def delete_update(id):
    """
    DELETE /updates/<id>
    Removes the document permanently.
    """
    obj_id = _parse_object_id(id)
    if obj_id is None:
        return jsonify({"message": "Invalid update ID"}), 400

    result = db.updates.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        return jsonify({"message": "Update not found"}), 404

    return jsonify({"message": "Update deleted successfully"}), 200


def toggle_pin(id):
    """
    PUT /updates/<id>/pin
    Flips the pinned boolean on the document.
    Returns the updated document.
    """
    obj_id = _parse_object_id(id)
    if obj_id is None:
        return jsonify({"message": "Invalid update ID"}), 400

    existing = db.updates.find_one({"_id": obj_id})
    if existing is None:
        return jsonify({"message": "Update not found"}), 404

    new_pinned = not existing.get("pinned", False)

    updated = db.updates.find_one_and_update(
        {"_id": obj_id},
        {"$set": {"pinned": new_pinned, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )

    action = "pinned" if new_pinned else "unpinned"
    return jsonify({
        "message": f"Update {action} successfully",
        "update": _serialize(updated),
    }), 200


# ── Public endpoints ─────────────────────────────────────────────────────────

def get_updates():
    """
    GET /updates
    Query params: ?status=  ?category=
    Pinned updates always appear first; within each group, newest first.
    """
    query = {}

    status_filter   = request.args.get("status",   "").strip()
    category_filter = request.args.get("category", "").strip()

    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({
                "message": f"Invalid status filter. Must be one of: {', '.join(VALID_STATUSES)}"
            }), 400
        query["status"] = status_filter

    if category_filter:
        if category_filter not in VALID_CATEGORIES:
            return jsonify({
                "message": f"Invalid category filter. Must be one of: {', '.join(VALID_CATEGORIES)}"
            }), 400
        query["category"] = category_filter

    cursor = db.updates.find(query).sort([
        ("pinned",     DESCENDING),
        ("created_at", DESCENDING),
    ])

    updates = [_serialize(doc) for doc in cursor]
    return jsonify({"updates": updates, "count": len(updates)}), 200


def get_stats():
    """
    GET /stats
    Returns:
      status_counts, category_counts, total,
      completion_percentage, current_streak, days_remaining
    """
    all_docs = list(db.updates.find({}))

    # Initialise counters
    status_counts   = {s: 0 for s in VALID_STATUSES}
    category_counts = {c: 0 for c in VALID_CATEGORIES}
    dates_with_activity: set[date] = set()

    for doc in all_docs:
        s = doc.get("status")
        c = doc.get("category")
        if s in status_counts:
            status_counts[s] += 1
        if c in category_counts:
            category_counts[c] += 1
        ts = doc.get("created_at")
        if isinstance(ts, datetime):
            dates_with_activity.add(ts.date())

    total      = len(all_docs)
    done_count = status_counts.get("done", 0)
    completion_percentage = round((done_count / total * 100), 1) if total > 0 else 0.0

    # Current streak: consecutive days ending today that each had ≥1 update
    streak     = 0
    check_date = date.today()
    while check_date in dates_with_activity:
        streak    += 1
        check_date -= timedelta(days=1)

    # Days remaining until END_DATE (clamped to 0)
    end_date_str  = os.getenv("END_DATE", "")
    days_remaining = 0
    if end_date_str:
        try:
            end_date       = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            days_remaining = max(0, (end_date - date.today()).days)
        except ValueError:
            days_remaining = 0

    return jsonify({
        "total":                total,
        "status_counts":        status_counts,
        "category_counts":      category_counts,
        "completion_percentage": completion_percentage,
        "current_streak":       streak,
        "days_remaining":       days_remaining,
    }), 200


def get_meta():
    """
    GET /meta
    Reads project info from environment variables and returns as JSON.
    """
    return jsonify({
        "project_name":   os.getenv("PROJECT_NAME",   ""),
        "team_name":      os.getenv("TEAM_NAME",      ""),
        "hackathon_name": os.getenv("HACKATHON_NAME", ""),
        "github_url":     os.getenv("GITHUB_URL",     ""),
    }), 200
