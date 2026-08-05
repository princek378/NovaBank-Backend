import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from database import db
from sqlalchemy import text

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

# ---------- DATABASE ----------
database_url = os.environ.get("DATABASE_URL", "").strip()

if not database_url:
    if os.environ.get("RENDER"):
        raise RuntimeError("DATABASE_URL is not set on Render. Add it in Environment.")
    database_url = "sqlite:///novabank.db"
    print("WARNING: Using local SQLite (dev only)")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if database_url.startswith("postgresql://") and "sslmode=" not in database_url:
    database_url += ("&" if "?" in database_url else "?") + "sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

db.init_app(app)
migrate = Migrate(app, db)

_safe_host = database_url.split("@")[-1] if "@" in database_url else database_url
print("Database host:", _safe_host)

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


@app.route("/api/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        db_type = "postgresql" if "postgresql" in database_url else "sqlite"
        return jsonify({
            "status": "ok",
            "database": db_type,
            "host": _safe_host,
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


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
    try:
        from sqlalchemy import inspect
        insp = inspect(db.engine)
        if "message" not in insp.get_table_names():
            return
        cols = [c["name"] for c in insp.get_columns("message")]
        if "is_read" not in cols:
            with db.engine.connect() as conn:
                conn.execute(
                    text("ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE")
                )
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
