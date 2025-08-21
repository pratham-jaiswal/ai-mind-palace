from handlers.agents.conversation_handler import ConversationHandler
from utils.auth_handlers import get_user_data
from controllers.utils import jsonify_error, jsonify_ok
from schemas.conversation import ConversationSchema, ConversationMetadataSchema
import traceback

class ConversationService:
    def get_conversations(conversation_id=None, jwt_bearer=None):
        try: 
            user_id = get_user_data(
                jwt_bearer=jwt_bearer
            ).get("user_id", None)
            if not user_id:
                return jsonify_error("Forbidden", 403)
            
            result = None
            if conversation_id:
                result = ConversationSchema(many=True).dump(
                    ConversationHandler(user_id=user_id).get_conversations_by_thread_id(
                        thread_id=conversation_id
                    )
                )
            else:
                result = ConversationMetadataSchema(many=True).dump(
                    ConversationHandler(user_id=user_id).get_all_conversation_threads()
                )
                for item in result:
                    item["title"] = item["thread_id"].replace(f"user-{user_id}--", "")

            return jsonify_ok(result)
        except Exception as e:
            traceback.print_exc()
            return jsonify_error("An error occurred while processing your request", 500)

    def delete_conversation(conversation_id, jwt_bearer=None):
        try:
            user_id = get_user_data(
                jwt_bearer=jwt_bearer
            ).get("user_id", None)
            if not user_id:
                return jsonify_error("Forbidden", 403)
            
            result = ConversationHandler(user_id=user_id).delete_conversations_by_thread_id(
                thread_id=conversation_id
            )

            return jsonify_ok({
                "deleted": result
            })
        except Exception as e:
            traceback.print_exc()
            return jsonify_error("An error occurred while processing your request", 500)

    def create_conversation(user_query, jwt_bearer=None):
        try:
            user_id = get_user_data(
                jwt_bearer=jwt_bearer
            ).get("user_id", None)
            if not user_id:
                return jsonify_error("Forbidden", 403)
            
            result = ConversationSchema().dump(
                ConversationHandler(user_id=user_id).create_conversation(
                    user_query=user_query
                )
            )

            return jsonify_ok(result)
        except Exception as e:
            traceback.print_exc()
            return jsonify_error("An error occurred while processing your request", 500)
