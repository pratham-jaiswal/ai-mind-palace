from flask import Blueprint, request
from services.chunk_service import ChunkService
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('chunks', __name__, url_prefix='/chunks')

@bp.route('/', methods=['POST'])
def create_chunk():
    data = request.get_json() or {}
    required = ['user_id', 'document_id', 'text']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    c = ChunkService.create(**data)
    return jsonify_ok(c.to_dict())

@bp.route('/<int:chunk_id>', methods=['GET'])
def get_chunk(chunk_id):
    c = ChunkService.get(chunk_id)
    if not c:
        return jsonify_error('not found', 404)
    return jsonify_ok(c.to_dict())

@bp.route('/', methods=['GET'])
def list_chunks():
    user_id = request.args.get('user_id')
    items = ChunkService.list(user_id=user_id)
    return jsonify_ok([i.to_dict() for i in items])

@bp.route('/<int:chunk_id>', methods=['PUT'])
def update_chunk(chunk_id):
    data = request.get_json() or {}
    c = ChunkService.update(chunk_id, **data)
    if not c:
        return jsonify_error('not found', 404)
    return jsonify_ok(c.to_dict())

@bp.route('/<int:chunk_id>', methods=['DELETE'])
def delete_chunk(chunk_id):
    ok = ChunkService.delete(chunk_id)
    if not ok:
        return jsonify_error('not found', 404)
    return jsonify_ok()
