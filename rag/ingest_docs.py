from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os

docs_path = "rag/docs"
texts = []

for file in os.listdir(docs_path):
    if file.endswith(".txt"):
        loader = TextLoader(os.path.join(docs_path, file))
        texts.extend(loader.load())

text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(texts)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(docs, embeddings)
db.save_local("rag/rag_db")
