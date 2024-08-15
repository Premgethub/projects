import os
from dotenv import load_dotenv
import chromadb
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

VECTOR_PERSIST_DIRECTORY = os.getenv("VECTOR_PERSIST_DIRECTORY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
TAG_NAME = os.getenv("TAG_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embeddings = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

client = chromadb.PersistentClient(path=VECTOR_PERSIST_DIRECTORY)
collection = client.get_or_create_collection(TAG_NAME)
vector_store = ChromaVectorStore(chroma_collection = collection)
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model = embeddings,
)

llm = Groq(model="mixtral-8x7b-32768", api_key = GROQ_API_KEY)

query_engine = index.as_query_engine(streaming=True,llm=llm)
response = query_engine.query("Give brief about NTRO?")
print(response)

