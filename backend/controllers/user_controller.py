from flask import Blueprint, request
from services.user_service import UserService
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    email = data.get('email')
    name = data.get('name')
    if not email:
        return jsonify_error('email is required')
    user = UserService.create(email=email, name=name)
    return jsonify_ok(user.to_dict())

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UserService.get(user_id)
    if not user:
        return jsonify_error('not found', 404)
    return jsonify_ok(user.to_dict())

@bp.route('/', methods=['GET'])
def list_users():
    users = UserService.list()
    return jsonify_ok([u.to_dict() for u in users])

@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json() or {}
    user = UserService.update(user_id, **data)
    if not user:
        return jsonify_error('not found', 404)
    return jsonify_ok(user.to_dict())

@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    ok = UserService.delete(user_id)
    if not ok:
        return jsonify_error('not found', 404)
    return jsonify_ok()
