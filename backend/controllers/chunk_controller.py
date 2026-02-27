from flask import Blueprint, request
from services.chunk_service import ChunkService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data

bp = Blueprint('chunks', __name__, url_prefix='/chunks')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['POST'])
@require_signed_in
def create_chunk():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    data['user_id'] = user_id
    required = ['user_id', 'document_id', 'text']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    c = ChunkService.create(**data)
    return jsonify_ok(c.to_dict())

@bp.route('/<int:chunk_id>', methods=['GET'])
@require_signed_in
def get_chunk(chunk_id):
    user_id = get_current_user_id()
    c = ChunkService.get(chunk_id)
    if not c or c.user_id != user_id:
        return jsonify_error('not found', 404)
    return jsonify_ok(c.to_dict())

@bp.route('/', methods=['GET'])
@require_signed_in
def list_chunks():
    user_id = get_current_user_id()
    items = ChunkService.list(user_id=user_id, limit=1000)
    return jsonify_ok([i.to_dict() for i in items])

@bp.route('/<int:chunk_id>', methods=['PUT'])
@require_signed_in
def update_chunk(chunk_id):
    user_id = get_current_user_id()
    c = ChunkService.get(chunk_id)
    if not c or c.user_id != user_id:
        return jsonify_error('not found', 404)
    data = request.get_json() or {}
    data.pop('user_id', None)
    c = ChunkService.update(chunk_id, **data)
    return jsonify_ok(c.to_dict())

@bp.route('/<int:chunk_id>', methods=['DELETE'])
@require_signed_in
def delete_chunk(chunk_id):
    user_id = get_current_user_id()
    c = ChunkService.get(chunk_id)
    if not c or c.user_id != user_id:
        return jsonify_error('not found', 404)
    ok = ChunkService.delete(chunk_id)
    return jsonify_ok() if ok else jsonify_error('not found', 404)
