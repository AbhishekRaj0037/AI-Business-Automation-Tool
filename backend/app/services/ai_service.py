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


vectorstore=PGVector(
connection_string=settings.DBUrl.replace("+asyncpg", ""),
embedding_function=embeddings,
collection_name="documents"
)