from handlers.vectorization.faiss_handler import FaissHandler
from handlers.vectorization.chunker import ChunkerHandler

class VectorMemoryTools:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def add_memory(self, text: str):
        """
        Add a text to the vector memory.
        
        Args:
            text (str): The text to be added to the vector memory.
            
        Returns:
            None
        """

        documents = ChunkerHandler(self.user_id).split_documents(text)
        memory_index = FaissHandler(self.user_id).create_faiss_index(documents)

        return memory_index

    def search_memory(self, query: str, source: str, k: int = 5):
        """
        Search the vector memory for relevant documents.
        
        Args:
            query (str): The search query.
            source (str): The source of the query.
            user_id (int): The ID of the user for whom the search is being performed.
            k (int): The number of top results to return.
            
        Returns:
            list: A list of the top k documents matching the query.
        """

        results = FaissHandler(self.user_id).search_faiss_index(query, source, k)
        return results
    