from flask import Blueprint, request
from services.project_service import ProjectService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data

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
    projects = ProjectService.list(user_id=user_id, limit=1000)
    return jsonify_ok([p.to_dict() for p in projects])

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
