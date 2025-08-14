from services.second_brain import get_response as get_response_service
from flask import Blueprint, request
from controllers.utils import jsonify_error
import uuid

bp = Blueprint('second_brain', __name__, url_prefix='/invoke')

@bp.route('/', methods=['POST'])
def get_response():
    data = request.get_json() or {}
    user_query = data.get('user_query', '')
    provider = data.get('provider', 'openai').lower()
    model = data.get('model', 'gpt-4.1-nano').lower()
    temperature = data.get('temperature', 0.3)
    thread_id = data.get('thread_id', str(uuid.uuid4()))
    timezone = data.get('timezone') # For example, 'Asia/Kolkata'
    debug = data.get('debug', False)

    if not user_query:
        return jsonify_error("User query is required", 400)
    
    if isinstance(temperature, float) and (temperature < 0 or temperature > 1):
        return jsonify_error("Temperature must be between 0 and 1", 400)

    response = get_response_service(
        user_query=user_query,
        provider=provider,
        model=model,
        temperature=temperature,
        thread_id=thread_id,
        timezone=timezone,
        debug=debug
    )
    
    return response
