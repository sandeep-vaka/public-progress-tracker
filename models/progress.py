from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

PROGRESS_STATUS = ("not_started", "in_progress", "completed")

class Progress(Document):
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    progress_status = StringField(required=True, choices=PROGRESS_STATUS, default="not_started")
    created_by = ReferenceField(User, required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {"collection": "progress"}

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "progress_status": self.progress_status,
            "created_by": self.created_by.to_dict() if self.created_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
