from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    minio_endpoint: str
    minio_console_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    secret_key: str

    class Config:
        env_file = ".env.docker"

settings = Settings()