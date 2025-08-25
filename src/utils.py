import os
from typing import List
from dotenv import load_dotenv

from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pinecone

load_dotenv()

# setting up env
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not PINECONE_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY or GEMINI_API_KEY in .env")

# ------------------------------------------------------------------

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_document",
    transport="rest",


)

INDEX_NAME = "llmvectordb" # name it into piencone after signing in and creating an index


def load_and_split_pdfs(pdf_dir: str, chunk_size: int = 800, chunk_overlap: int = 50) -> List[Document]:
    """Load PDFs from directory and return LangChain Document chunks."""
    loader = PyPDFDirectoryLoader(pdf_dir)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    return chunks


def get_or_create_vectorstore(chunks: List[Document]) -> PineconeVectorStore:
    """
    If the index exists, return existing vectorstore; otherwise create it.
    This makes `quiz.py` idempotent.
    """
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=pinecone.ServerlessSpec(cloud="aws", region="us-west-2")
        )
        while not pc.describe_index(INDEX_NAME).status['ready']:
            import time
            time.sleep(2)

        vectorstore = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            index_name=INDEX_NAME
        )
    else:
        vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
    return vectorstore