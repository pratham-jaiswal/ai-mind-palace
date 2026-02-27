from flask import Blueprint, request
from services.person_service import PersonService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data

bp = Blueprint('people', __name__, url_prefix='/people')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['POST'])
@require_signed_in
def create_person():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    data['user_id'] = user_id
    required = ['user_id', 'name']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    p = PersonService.create(**data)
    return jsonify_ok(p.to_dict())

@bp.route('/<int:person_id>', methods=['GET'])
@require_signed_in
def get_person(person_id):
    user_id = get_current_user_id()
    p = PersonService.get(person_id)
    if not p or p.user_id != user_id:
        return jsonify_error('not found', 404)
    return jsonify_ok(p.to_dict())

@bp.route('/', methods=['GET'])
@require_signed_in
def list_people():
    user_id = get_current_user_id()
    items = PersonService.list(user_id=user_id, limit=1000)
    return jsonify_ok([i.to_dict() for i in items])

@bp.route('/<int:person_id>', methods=['PUT'])
@require_signed_in
def update_person(person_id):
    user_id = get_current_user_id()
    p = PersonService.get(person_id)
    if not p or p.user_id != user_id:
        return jsonify_error('not found', 404)
    data = request.get_json() or {}
    # remove user_id if passed to prevent reassignment
    data.pop('user_id', None)
    p = PersonService.update(person_id, **data)
    return jsonify_ok(p.to_dict())

@bp.route('/<int:person_id>', methods=['DELETE'])
@require_signed_in
def delete_person(person_id):
    user_id = get_current_user_id()
    p = PersonService.get(person_id)
    if not p or p.user_id != user_id:
        return jsonify_error('not found', 404)
    ok = PersonService.delete(person_id)
    return jsonify_ok() if ok else jsonify_error('not found', 404)
