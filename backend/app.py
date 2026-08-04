import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from database import db

from models.user import User
from models.account import Account
from models.transaction import Transaction
from models.admin_settings import AdminSettings
from models.message import Message
from models.notification import Notification

from routes.account_routes import account_bp
from routes.transaction_routes import transaction_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.customer_routes import customer_bp
from routes.chat_routes import chat_bp
from routes.settings_routes import settings_bp
from routes.report_routes import report_bp
from routes.notification_routes import notification_bp

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Use DATABASE_URL from environment (Neon / Render). Fallback to SQLite for local only.
database_url = os.environ.get("DATABASE_URL", "sqlite:///novabank.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "novabank-secret-key-change-in-production"
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(report_bp)
app.register_blueprint(notification_bp)

@app.route("/")
def home():
    return jsonify({"message": "NovaBank API Running", "status": "ok"})

@app.errorhandler(Exception)
def handle_error(error):
    print(error)
    return {"error": str(error)}, 500

def seed_default_admin():
    admin = User.query.filter_by(role="Admin").first()
    if not admin:
        admin = User(
            name="Administrator",
            email="admin@novabank.com",
            password=generate_password_hash("12345678"),
            role="Admin",
            status="Active",
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created → email: admin@novabank.com  password: 12345678")
    else:
        print("Admin already exists")

def ensure_message_columns():
    """Add is_read column if missing (works on SQLite; safe no-op on Postgres)."""
    try:
        from sqlalchemy import text, inspect
        insp = inspect(db.engine)
        if "message" not in insp.get_table_names():
            return
        cols = [c["name"] for c in insp.get_columns("message")]
        if "is_read" not in cols:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("Added is_read column to message table")
    except Exception as e:
        print("ensure_message_columns:", e)

with app.app_context():
    db.create_all()
    ensure_message_columns()
    seed_default_admin()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
