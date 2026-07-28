from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Customer Analytics API"
    API_V1_STR: str = "/api/v1"

    # CORS Origins
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:4000",
        "http://127.0.0.1:4000",
    ]


settings = Settings()
