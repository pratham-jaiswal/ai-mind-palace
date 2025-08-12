from flask import Blueprint, request
from services.document_service import DocumentService
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/', methods=['POST'])
def create_document():
    data = request.get_json() or {}
    required = ['user_id']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    doc = DocumentService.create(**data)
    return jsonify_ok(doc.to_dict())

@bp.route('/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    doc = DocumentService.get(doc_id)
    if not doc:
        return jsonify_error('not found', 404)
    return jsonify_ok(doc.to_dict())

@bp.route('/', methods=['GET'])
def list_documents():
    user_id = request.args.get('user_id')
    docs = DocumentService.list(user_id=user_id)
    return jsonify_ok([d.to_dict() for d in docs])

@bp.route('/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    data = request.get_json() or {}
    doc = DocumentService.update(doc_id, **data)
    if not doc:
        return jsonify_error('not found', 404)
    return jsonify_ok(doc.to_dict())

@bp.route('/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    ok = DocumentService.delete(doc_id)
    if not ok:
        return jsonify_error('not found', 404)
    return jsonify_ok()
