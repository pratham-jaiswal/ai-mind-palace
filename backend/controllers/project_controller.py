from flask import Blueprint, request
from services.project_service import ProjectService
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/', methods=['POST'])
def create_project():
    data = request.get_json() or {}
    required = ['user_id', 'title']
    for r in required:
        if r not in data:
            return jsonify_error(f'{r} is required')
    proj = ProjectService.create(**data)
    return jsonify_ok(proj.to_dict())

@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    proj = ProjectService.get(project_id)
    if not proj:
        return jsonify_error('not found', 404)
    return jsonify_ok(proj.to_dict())

@bp.route('/', methods=['GET'])
def list_projects():
    user_id = request.args.get('user_id')
    projects = ProjectService.list(user_id=user_id)
    return jsonify_ok([p.to_dict() for p in projects])

@bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json() or {}
    proj = ProjectService.update(project_id, **data)
    if not proj:
        return jsonify_error('not found', 404)
    return jsonify_ok(proj.to_dict())

@bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    ok = ProjectService.delete(project_id)
    if not ok:
        return jsonify_error('not found', 404)
    return jsonify_ok()
