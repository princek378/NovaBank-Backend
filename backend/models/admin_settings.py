from database import db
from datetime import datetime


class AdminSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), default="Administrator")
    email = db.Column(db.String(120), default="admin@novabank.com")
    bank_name = db.Column(db.String(100), default="NovaBank")
    currency = db.Column(db.String(10), default="USD")

    # Transfer security codes
    imf_code = db.Column(db.String(50), default="IMF-0000")
    cot_code = db.Column(db.String(50), default="COT-0000")
    require_imf = db.Column(db.Boolean, default=True)
    require_cot = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
