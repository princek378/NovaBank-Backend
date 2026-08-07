from database import db
from datetime import datetime


class OtpCode(db.Model):
    __tablename__ = "otp_code"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    purpose = db.Column(db.String(30), nullable=False)  # register | reset
    payload = db.Column(db.Text, nullable=True)  # JSON for pending registration
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
