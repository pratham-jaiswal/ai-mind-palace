from flask import Blueprint, request
from services.document_service import DocumentService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data

bp = Blueprint('documents', __name__, url_prefix='/documents')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['POST'])
@require_signed_in
def create_document():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    data['user_id'] = user_id
    required = ['user_id']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    doc = DocumentService.create(**data)
    return jsonify_ok(doc.to_dict())

@bp.route('/<int:doc_id>', methods=['GET'])
@require_signed_in
def get_document(doc_id):
    user_id = get_current_user_id()
    doc = DocumentService.get(doc_id)
    if not doc or doc.user_id != user_id:
        return jsonify_error('not found', 404)
    return jsonify_ok(doc.to_dict())

@bp.route('/', methods=['GET'])
@require_signed_in
def list_documents():
    user_id = get_current_user_id()
    docs = DocumentService.list(user_id=user_id, limit=1000)
    return jsonify_ok([d.to_dict() for d in docs])

@bp.route('/<int:doc_id>', methods=['PUT'])
@require_signed_in
def update_document(doc_id):
    user_id = get_current_user_id()
    doc = DocumentService.get(doc_id)
    if not doc or doc.user_id != user_id:
        return jsonify_error('not found', 404)
    data = request.get_json() or {}
    data.pop('user_id', None)
    doc = DocumentService.update(doc_id, **data)
    return jsonify_ok(doc.to_dict())

@bp.route('/<int:doc_id>', methods=['DELETE'])
@require_signed_in
def delete_document(doc_id):
    user_id = get_current_user_id()
    doc = DocumentService.get(doc_id)
    if not doc or doc.user_id != user_id:
        return jsonify_error('not found', 404)
    ok = DocumentService.delete(doc_id)
    return jsonify_ok() if ok else jsonify_error('not found', 404)
