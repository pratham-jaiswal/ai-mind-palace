from handlers.agents.mind_palace_handler import MindPalaceHandler
from controllers.utils import jsonify_error, jsonify_ok
import traceback
import os
from jose import jwt
from services.user_service import UserService

def get_response(user_query: str, timezone: str, thread_id: str, 
                 provider: str = "openai", model: str = "gpt-4.1-nano", 
                 temperature: float = 0.3, debug: bool = False,
                 jwt_bearer: str = None) -> str:
    """
    Get a response from the mind palace agent based on the user's query.
    
    Args:
        user_query: The query from the user.
        provider: The LLM provider to use.
        model: The model to use for the agent.
        temperature: The temperature for the model.
        debug: If True, enables debug mode.
    
    Returns:
        The response from the mind palace agent.
    """
    try:
        from clerk_backend_api import Clerk

        with Clerk(bearer_auth=os.getenv('CLERK_SECRET_KEY'), ) as clerk:

            jwks = clerk.jwks.get_jwks()

            assert jwks is not None

            header = jwt.get_unverified_header(jwt_bearer)

            key = next((k for k in jwks.keys if k.kid == header["kid"]), None)
            if not key:
                raise Exception("Public key not found in Clerk JWKS")

            decoded_jwt = jwt.decode(
                jwt_bearer,
                key.model_dump(),
                algorithms=[header["alg"]],
            )
            clerk_id = decoded_jwt["user_id"]
            user = UserService.get_by_clerk_id(clerk_id)
            user_id = user.id if user else None
    
        if not user_id:
            return jsonify_error("Forbidden", 403)
        
        result = MindPalaceHandler(user_id=user_id).use_mind_palace(
            user_query=user_query, 
            provider=provider, 
            model=model, 
            temperature=temperature, 
            thread_id=thread_id,
            timezone=timezone,
            debug=debug
        )
        return jsonify_ok(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify_error("An error occurred while processing your request", 500)
