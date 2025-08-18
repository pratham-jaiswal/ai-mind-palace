from flask import Blueprint, request
from controllers.utils import jsonify_ok
from utils.auth_middleware import require_signed_in
from services.conversation_service import ConversationService

bp = Blueprint('conversations', __name__, url_prefix='/conversation')

@bp.route('/fetch', methods=['GET'])
@bp.route('/fetch/<conversation_id>', methods=['GET'])
@require_signed_in
def fetch(conversation_id=None):
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]

    return ConversationService.get_conversations(
        conversation_id=conversation_id,
        jwt_bearer=jwt_bearer
    )

@bp.route('/create', methods=['POST'])
@require_signed_in
def create_conversation():
    data = request.get_json() or {}
    conversation_id = data.get('conversation_id')
    
    return ConversationService.create_conversation(
        conversation_id=conversation_id
    )

@bp.route('/delete', methods=['DELETE'])
@require_signed_in
def delete_conversation():
    data = request.get_json() or {}
    conversation_id = data.get('conversation_id')

    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]

    return ConversationService.delete_conversation(
        conversation_id=conversation_id,
        jwt_bearer=jwt_bearer
    )
