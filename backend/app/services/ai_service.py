from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from app.config import settings

llm = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=settings.GPT_MINI,
    base_url="https://models.github.ai/inference",
)
 
splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)

embeddings = OpenAIEmbeddings(
    model="openai/text-embedding-3-small",
    api_key=settings.EMB3_SMALL,
    base_url="https://models.github.ai/inference",
    tiktoken_model_name="text-embedding-3-small",
    check_embedding_ctx_length=False,
)


_db_url = settings.DBUrl.replace("+asyncpg", "")
_vectorstore_cache: dict[str, PGVector] = {}


def get_user_vectorstore(user_id: str) -> PGVector:
    if user_id not in _vectorstore_cache:
        _vectorstore_cache[user_id] = PGVector(
            connection_string=_db_url,
            embedding_function=embeddings,
            collection_name=f"user_{user_id}",
        )
    return _vectorstore_cache[user_id]