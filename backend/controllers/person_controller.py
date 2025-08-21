# from flask import Blueprint, request
# from services.person_service import PersonService
# from controllers.utils import jsonify_ok, jsonify_error

# bp = Blueprint('people', __name__, url_prefix='/people')

# @bp.route('/', methods=['POST'])
# def create_person():
#     data = request.get_json() or {}
#     required = ['user_id', 'name']
#     for r in required:
#         if r not in data:
#             return jsonify_error(f'{r} is required')
#     p = PersonService.create(**data)
#     return jsonify_ok(p.to_dict())

# @bp.route('/<int:person_id>', methods=['GET'])
# def get_person(person_id):
#     p = PersonService.get(person_id)
#     if not p:
#         return jsonify_error('not found', 404)
#     return jsonify_ok(p.to_dict())

# @bp.route('/', methods=['GET'])
# def list_people():
#     user_id = request.args.get('user_id')
#     items = PersonService.list(user_id=user_id)
#     return jsonify_ok([i.to_dict() for i in items])

# @bp.route('/<int:person_id>', methods=['PUT'])
# def update_person(person_id):
#     data = request.get_json() or {}
#     p = PersonService.update(person_id, **data)
#     if not p:
#         return jsonify_error('not found', 404)
#     return jsonify_ok(p.to_dict())

# @bp.route('/<int:person_id>', methods=['DELETE'])
# def delete_person(person_id):
#     ok = PersonService.delete(person_id)
#     if not ok:
#         return jsonify_error('not found', 404)
#     return jsonify_ok()
