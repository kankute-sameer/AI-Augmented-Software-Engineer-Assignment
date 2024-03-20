from langchain_community.vectorstores import Chroma
import chromadb
from langchain_openai import OpenAIEmbeddings
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def chroma_client(texts):
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings()

    # Create an ephemeral (in-memory) Chroma client
    new_client = chromadb.EphemeralClient()

    # Load documents into Chroma with OpenAI embeddings
    openai_lc_client = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        client=new_client,
        collection_name="openai_collection"
    )

    return openai_lc_client