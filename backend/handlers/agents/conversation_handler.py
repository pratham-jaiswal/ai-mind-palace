from models import db, Conversation
from typing import Literal

class ConversationHandler:
    def __init__(self, user_id):
        self.user_id = user_id

    def create_conversation(self, thread_id: str, message: str, sender: Literal["user", "ai"]) -> Conversation:
        """
        Create a new conversation for the user.

        Args:
            thread_id (str): The ID of the conversation thread.
            message (str): The content of the message.
            sender (Literal["user", "ai"]): The sender of the message, either the user or an AI.

        Returns:
            Conversation: The newly created conversation object.
        """

        conversation = Conversation(user_id=self.user_id, thread_id=thread_id, message=message, sender=sender)
        db.session.add(conversation)
        db.session.commit()
        return conversation

    def get_conversations_by_thread_id(self, thread_id: str) -> list[Conversation]:
        """
        Get all conversations for a specific thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.

        Returns:
            List[Conversation]: A list of user's conversation objects for the given thread ID.
        """
        return Conversation.query.filter_by(thread_id=thread_id, user_id=self.user_id).all()
    
    def get_all_conversations(self):
        """
        Get all conversations for the user.

        Returns:
            List[Conversation]: A list of user's conversation objects.
        """
        return Conversation.query.filter_by(user_id=self.user_id).all()

    def delete_conversations_by_thread_id(self, thread_id: str):
        """
        Delete all conversations for a specific thread ID.

        Args:
            thread_id (str): The ID of the conversation thread.
        """
        conversations = self.get_conversations_by_thread_id(thread_id)
        if not conversations:
            return False
        for c in conversations:
            db.session.delete(c)
        db.session.commit()
        return True
