from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=5
)

class ChunkerHandler:
    def __init__(self, user_id):
        self.user_id = user_id

    def split_documents(self, text: str, source: str = "user_input") -> list:
        """
        Split documents into smaller chunks using a text splitter.
        
        Args:
            text (str): The text to be split.
            source (str): The source of the text, default is "user_input".
            
        Returns:
            list: A list of text chunks after splitting the documents.
        """

        texts = text_splitter.split_text(text)
        text_docs = []
        for i, text in enumerate(texts):
            text_docs.append(Document(page_content=text.strip(), metadata={"source": source, "user_id": self.user_id}))
        
        return text_docs
