from flask import Blueprint, request
from services.decision_service import DecisionService
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('decisions', __name__, url_prefix='/decisions')

@bp.route('/', methods=['POST'])
def create_decision():
    data = request.get_json() or {}
    required = ['user_id', 'decision_text']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    d = DecisionService.create(**data)
    return jsonify_ok(d.to_dict())

@bp.route('/<int:decision_id>', methods=['GET'])
def get_decision(decision_id):
    d = DecisionService.get(decision_id)
    if not d:
        return jsonify_error('not found', 404)
    return jsonify_ok(d.to_dict())

@bp.route('/', methods=['GET'])
def list_decisions():
    user_id = request.args.get('user_id')
    items = DecisionService.list(user_id=user_id)
    return jsonify_ok([i.to_dict() for i in items])

@bp.route('/<int:decision_id>', methods=['PUT'])
def update_decision(decision_id):
    data = request.get_json() or {}
    d = DecisionService.update(decision_id, **data)
    if not d:
        return jsonify_error('not found', 404)
    return jsonify_ok(d.to_dict())

@bp.route('/<int:decision_id>', methods=['DELETE'])
def delete_decision(decision_id):
    ok = DecisionService.delete(decision_id)
    if not ok:
        return jsonify_error('not found', 404)
    return jsonify_ok()
