from flask import Blueprint, request
from services.user_service import UserService
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import clerk_webhook_required

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/', methods=['POST'])
@clerk_webhook_required
def manage_user():
    res = request.get_json() or {}
    data = res.get('data', {})
    clerk_id = data.get('id')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    name = f'{first_name} {last_name}'
        
    webhook_type = res.get('type')
    primary_email_address_id = data.get('primary_email_address_id')
    email_addresses = data.get('email_addresses', [])

    email = ''
    for email_data in email_addresses:
        if email_data.get('id', '') == primary_email_address_id:
            email = email_data.get('email_address', '')
            break

    if webhook_type == 'user.created':
        if not name:
            return jsonify_error('No "name" associated with your account.')
        if not email:
            return jsonify_error('email is required')
        user = UserService.create(
            email=email, 
            name=name, 
            additional_info={
                'clerk_id': clerk_id
            }
        )
        return jsonify_ok(user.to_dict())
    elif webhook_type == 'user.updated':
        if not name:
            return jsonify_error('No "name" associated with your account.')
        if not email:
            return jsonify_error('email is required')
        user = UserService.update(
            email=email, 
            name=name, 
            clerk_id=clerk_id
        )
        return jsonify_ok(user.to_dict())
    elif webhook_type == 'user.deleted':
        ok = UserService.delete(clerk_id)
        return jsonify_ok({
            "deleted": ok
        })
    return jsonify_error('Invalid webhook type')
