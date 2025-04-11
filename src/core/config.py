class Settings:
    PROJECT_NAME: str = "FastAPI Todo App"
    SECRET_KEY: str = "super-secure-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
