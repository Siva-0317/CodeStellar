# rag/ingest_docs.py
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os

def ingest_docs():
    all_files = ["docs/" + f for f in os.listdir("docs") if f.endswith(".txt")]
    all_docs = []

    for path in all_files:
        loader = TextLoader(path)
        docs = loader.load()
        all_docs.extend(docs)

    splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents(all_docs)

    vectordb = Chroma.from_documents(chunks, embedding=OpenAIEmbeddings(), persist_directory="rag_db")
    vectordb.persist()

if __name__ == "__main__":
    ingest_docs()
