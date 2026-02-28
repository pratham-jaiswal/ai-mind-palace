from flask import Blueprint, request
from services.project_service import ProjectService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data
from models.project import Project

bp = Blueprint('projects', __name__, url_prefix='/projects')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['POST'])
@require_signed_in
def create_project():
    user_id = get_current_user_id()
    data = request.get_json() or {}
    data['user_id'] = user_id
    required = ['user_id', 'title']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    proj = ProjectService.create(**data)
    return jsonify_ok(proj.to_dict())

@bp.route('/<int:project_id>', methods=['GET'])
@require_signed_in
def get_project(project_id):
    user_id = get_current_user_id()
    proj = ProjectService.get(project_id)
    if not proj or proj.user_id != user_id:
        return jsonify_error('not found', 404)
    return jsonify_ok(proj.to_dict())

@bp.route('/', methods=['GET'])
@require_signed_in
def list_projects():
    user_id = get_current_user_id()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    query = Project.query.filter_by(user_id=user_id)
    
    q = request.args.get('q', '').strip()
    if q:
        from sqlalchemy import func, or_
        search_term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Project.title).like(search_term),
                func.lower(Project.description).like(search_term)
            )
        )
    total = query.count()
    projects = query.order_by(Project.id.desc()).offset(offset).limit(limit).all()
    
    return jsonify_ok({
        "result": [p.to_dict() for p in projects],
        "total": total,
        "page": page,
        "limit": limit
    })

@bp.route('/<int:project_id>', methods=['PUT'])
@require_signed_in
def update_project(project_id):
    user_id = get_current_user_id()
    proj = ProjectService.get(project_id)
    if not proj or proj.user_id != user_id:
        return jsonify_error('not found', 404)
    data = request.get_json() or {}
    data.pop('user_id', None)
    proj = ProjectService.update(project_id, **data)
    return jsonify_ok(proj.to_dict())

@bp.route('/<int:project_id>', methods=['DELETE'])
@require_signed_in
def delete_project(project_id):
    user_id = get_current_user_id()
    proj = ProjectService.get(project_id)
    if not proj or proj.user_id != user_id:
        return jsonify_error('not found', 404)
    ok = ProjectService.delete(project_id)
    return jsonify_ok() if ok else jsonify_error('not found', 404)
