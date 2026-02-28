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
        import os
        index_path = os.path.join(FAISS_INDEX_DIR, "index.faiss")
        
        if os.path.exists(index_path):
            existing_index = FAISS.load_local(FAISS_INDEX_DIR, embedder, allow_dangerous_deserialization=True)
            new_index = FAISS.from_documents(documents, embedder)
            existing_index.merge_from(new_index)
            existing_index.save_local(FAISS_INDEX_DIR)
            return existing_index
        else:
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
        faiss_index = FAISS.load_local(FAISS_INDEX_DIR, embedder, allow_dangerous_deserialization=True)
        
        search_filter = {"user_id": self.user_id}
        if source:
            search_filter["source"] = source
            
        results = faiss_index.similarity_search(
            query,
            k=k,
            filter=search_filter
        )

        return results

    def get_all_documents(self) -> list:
        """
        Retrieve all documents for the user from the FAISS index.
        
        Returns:
            list: A list of all documents belonging to the user.
        """
        # load_local parameter allow_dangerous_deserialization might be required for recent langchain versions, 
        # but to match existing codebase usage we continue without it if not specified earlier.
        # Actually it is specified now because it crashes otherwise.
        faiss_index = FAISS.load_local(FAISS_INDEX_DIR, embedder, allow_dangerous_deserialization=True)
        
        user_docs = []
        for doc_id, doc in faiss_index.docstore._dict.items():
            if doc.metadata.get("user_id") == self.user_id:
                # Inject the hidden FAISS UUID into the metadata dictionary so it can be passed to the frontend
                doc.metadata["id"] = doc_id
                user_docs.append(doc)
                
        return user_docs

    def delete_document(self, doc_id: str) -> bool:
        """
        Deletes a specific document from the FAISS index by its internal UUID.
        
        Args:
            doc_id (str): The internal FAISS UUID of the document.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        import os
        index_path = os.path.join(FAISS_INDEX_DIR, "index.faiss")
        
        if not os.path.exists(index_path):
            return False
            
        try:
            faiss_index = FAISS.load_local(FAISS_INDEX_DIR, embedder, allow_dangerous_deserialization=True)
            faiss_index.delete([doc_id])
            faiss_index.save_local(FAISS_INDEX_DIR)
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id} from FAISS index: {e}")
            return False
