from flask import Blueprint, request
from services.person_service import PersonService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data
from models.person import Person

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

@bp.route('/self', methods=['GET'])
@require_signed_in
def get_self():
    user_id = get_current_user_id()
    # Find a Person where name is 'self' or 'me'
    from sqlalchemy import func
    p = Person.query.filter(
        Person.user_id == user_id,
        func.lower(Person.name).in_(['self', 'me'])
    ).first()
    
    if not p:
        return jsonify_error('not found', 404)
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
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    from sqlalchemy import func, or_
    query = Person.query.filter(
        Person.user_id == user_id,
        func.lower(Person.name).notin_(['self', 'me'])
    )
    
    q = request.args.get('q', '').strip()
    if q:
        search_term = f"%{q.lower()}%"
        # We search by name or see if it's anywhere in notes (cast as string might vary by DB, but typically works or we search JSON if notes is JSON)
        # Using basic cast to string for the array column
        from sqlalchemy import cast, String
        query = query.filter(
            or_(
                func.lower(Person.name).like(search_term),
                cast(Person.notes, String).ilike(search_term)
            )
        )
        
    total = query.count()
    items = query.order_by(Person.id.desc()).offset(offset).limit(limit).all()
    
    return jsonify_ok({
        "result": [i.to_dict() for i in items],
        "total": total,
        "page": page,
        "limit": limit
    })

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
