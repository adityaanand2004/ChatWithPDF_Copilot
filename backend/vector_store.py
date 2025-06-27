import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(embedding_function=embedding, persist_directory="chroma_db")

def store_document(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents([Document(page_content=text)])
    db.add_documents(docs)
    db.persist()

def retrieve_context(query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([doc.page_content for doc in docs])
