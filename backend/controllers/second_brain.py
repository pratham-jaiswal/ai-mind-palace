from services.second_brain import get_response
from flask import Blueprint, request
from controllers.utils import jsonify_ok, jsonify_error

bp = Blueprint('second_brain', __name__, url_prefix='/invoke')

@bp.route('/', methods=['POST'])
def get_response():
    data = request.get_json() or {}
    user_query = data.get('user_query', '')
    provider = data.get('provider', 'openai')
    model = data.get('model', 'gpt-4.1-nano')
    temperature = data.get('temperature', 0.3)
    debug = data.get('debug', False)

    if not user_query:
        return jsonify_error("User query is required", 400)

    response = get_response(
        user_query=user_query,
        provider=provider,
        model=model,
        temperature=temperature,
        debug=debug
    )
    
    return jsonify_ok({"response": response})