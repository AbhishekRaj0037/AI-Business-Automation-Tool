from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DBUrl:str
    SQLAlchemyJobStore:str
    JWT_SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:str
    REFRESH_TOKEN_EXPIRE_MINUTES:str
    GPT_MINI:str
    EMB3_SMALL:str
    VECTOR_DB:str
    aws_access_key:str
    aws_secret_key:str
    aws_region:str
    cloud_name:str
    api_key:str
    api_secret:str
    client_id:str
    client_secret:str
    Redis_DB:str

    model_config = {"env_file": Path(__file__).parent / ".env"}



settings=Settings()
