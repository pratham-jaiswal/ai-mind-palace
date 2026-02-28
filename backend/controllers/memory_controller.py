from flask import Blueprint, request
from controllers.utils import jsonify_ok, jsonify_error
from utils.auth_middleware import require_signed_in
from utils.auth_handlers import get_user_data
from handlers.tools.vector_memory import VectorMemoryTools

bp = Blueprint('memories', __name__, url_prefix='/memories')

def get_current_user_id():
    headers = request.headers
    jwt_bearer = headers.get('Authorization', '').split(' ')[1]
    return get_user_data(jwt_bearer=jwt_bearer).get("user_id")

@bp.route('/', methods=['GET'])
@require_signed_in
def list_memories():
    user_id = get_current_user_id()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    q = request.args.get('q', '').strip()
    
    try:
        tools = VectorMemoryTools(user_id)
        if q:
            # When searching semantically, we don't necessarily want to reverse chronology
            # as FAISS returns them by relevance score.
            all_memories = tools.search_memory(q, limit=100)
            if all_memories is None:
                all_memories = []
        else:
            all_memories = tools.get_all_memories()
            if all_memories is None:
                all_memories = []
            all_memories.reverse()
            
        total = len(all_memories)
        
        # Paginate the list of Document objects
        paginated_docs = all_memories[offset:offset+limit]
        
        # Convert Document objects to dicts
        result = []
        for doc in paginated_docs:
            result.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return jsonify_ok({
            "result": result,
            "total": total,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify_error(str(e))

@bp.route('/', methods=['POST'])
@require_signed_in
def add_memory():
    user_id = get_current_user_id()
    data = request.json
    content = data.get('content')
    
    if not content:
        return jsonify_error("Memory content is required.")
        
    try:
        # source = "user_input" is automatically assigned inside ChunkerHandler
        VectorMemoryTools(user_id).add_memory(content)
        return jsonify_ok()
    except Exception as e:
        return jsonify_error(str(e))

@bp.route('/<memory_id>', methods=['DELETE'])
@require_signed_in
def delete_memory(memory_id):
    user_id = get_current_user_id()
    try:
        success = VectorMemoryTools(user_id).delete_memory(memory_id)
        if success:
            return jsonify_ok()
        else:
            return jsonify_error("Failed to delete memory.")
    except Exception as e:
        return jsonify_error(str(e))
        
@bp.route('/<memory_id>', methods=['PUT'])
@require_signed_in
def update_memory(memory_id):
    user_id = get_current_user_id()
    data = request.json
    content = data.get('content')
    
    if not content:
        return jsonify_error("Memory content is required.")
        
    try:
        # FAISS editing requires deletion of the old embedding UUID and immediate generation of a new one.
        VectorMemoryTools(user_id).delete_memory(memory_id)
        VectorMemoryTools(user_id).add_memory(content)
        return jsonify_ok()
    except Exception as e:
        return jsonify_error(str(e))
