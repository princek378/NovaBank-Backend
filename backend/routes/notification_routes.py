from flask import Blueprint, jsonify, request
from database import db
from models.notification import Notification

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notification_bp.route('/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    items = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'read': n.is_read,
        'date': n.created_at.isoformat()
    } for n in items])

@notification_bp.route('/<int:user_id>', methods=['POST'])
def create_notification(user_id):
    data=request.get_json() or {}
    n=Notification(user_id=user_id,title=data.get('title','NovaBank Alert'),message=data.get('message',''))
    db.session.add(n)
    db.session.commit()
    return jsonify({'message':'Notification created'}),201

@notification_bp.route('/read/<int:id>', methods=['PUT'])
def mark_read(id):
    n=Notification.query.get(id)
    if not n:
        return jsonify({'message':'Not found'}),404
    n.is_read=True
    db.session.commit()
    return jsonify({'message':'Updated'})
