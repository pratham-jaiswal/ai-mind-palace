from flask import Blueprint, request
from services.decision_service import DecisionService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data
from models.decision import Decision

bp = Blueprint('decisions', __name__, url_prefix='/decisions')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['POST'])
@require_signed_in
def create_decision():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    data['user_id'] = user_id
    required = ['user_id', 'decision_text']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    d = DecisionService.create(**data)
    return jsonify_ok(d.to_dict())

@bp.route('/<int:decision_id>', methods=['GET'])
@require_signed_in
def get_decision(decision_id):
    user_id = get_current_user_id()
    d = DecisionService.get(decision_id)
    if not d or d.user_id != user_id:
        return jsonify_error('not found', 404)
    return jsonify_ok(d.to_dict())

@bp.route('/', methods=['GET'])
@require_signed_in
def list_decisions():
    user_id = get_current_user_id()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    query = Decision.query.filter_by(user_id=user_id)
    
    q = request.args.get('q', '').strip()
    if q:
        from sqlalchemy import func, or_
        search_term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Decision.decision_name).like(search_term),
                func.lower(Decision.decision_text).like(search_term)
            )
        )
    total = query.count()
    items = query.order_by(Decision.id.desc()).offset(offset).limit(limit).all()
    
    return jsonify_ok({
        "result": [i.to_dict() for i in items],
        "total": total,
        "page": page,
        "limit": limit
    })

@bp.route('/<int:decision_id>', methods=['PUT'])
@require_signed_in
def update_decision(decision_id):
    user_id = get_current_user_id()
    d = DecisionService.get(decision_id)
    if not d or d.user_id != user_id:
        return jsonify_error('not found', 404)
    data = request.get_json() or {}
    data.pop('user_id', None)
    d = DecisionService.update(decision_id, **data)
    return jsonify_ok(d.to_dict())

@bp.route('/<int:decision_id>', methods=['DELETE'])
@require_signed_in
def delete_decision(decision_id):
    user_id = get_current_user_id()
    d = DecisionService.get(decision_id)
    if not d or d.user_id != user_id:
        return jsonify_error('not found', 404)
    ok = DecisionService.delete(decision_id)
    return jsonify_ok() if ok else jsonify_error('not found', 404)
