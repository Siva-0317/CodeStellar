from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def query_docs(query):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="rag_db", embedding_function=embeddings)
    results = db.similarity_search(query, k=2)
    return [r.page_content for r in results]
