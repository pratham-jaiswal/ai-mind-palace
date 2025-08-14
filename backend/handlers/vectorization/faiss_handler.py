from langchain_community.vectorstores import FAISS
from .openai_embeddings import embedder
from utils.env_vars import FAISS_INDEX_DIR

class FaissHandler:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def create_faiss_index(self, documents) -> FAISS:
        """
        Create a FAISS index from the provided documents using OpenAI embeddings.
        
        Args:
            documents (list): A list of documents to be indexed.
            
        Returns:
            FAISS: A FAISS index containing the embedded documents.
        """
        
        faiss_index = FAISS.from_documents(documents, embedder)
        faiss_index.save_local(FAISS_INDEX_DIR)
        return faiss_index

    def search_faiss_index(self, query: str, source: str, k: int = 5) -> list:
        """
        Search the FAISS index for the most relevant documents to the query.
        
        Args:
            query (str): The search query.
            k (int): The number of top results to return.
            
        Returns:
            list: A list of the top k documents matching the query.
        """
        faiss_index = FAISS.load_local(FAISS_INDEX_DIR, embedder)
        results = faiss_index.similarity_search(
            query,
            k=k,
            filter={
                "source": source,
                "user_id": self.user_id,
            },
        )

        return results
