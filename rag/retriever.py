from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local("rag/rag_db", embeddings)
    return db

def retrieve_explanation(query: str, k=3):
    db = load_vectorstore()
    return db.similarity_search(query, k)
