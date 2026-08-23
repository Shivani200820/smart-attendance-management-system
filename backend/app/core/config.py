from urllib.parse import quote_plus
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "attendance_management"
    
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    JWT_SECRET_KEY: str = "dev_jwt_secret_key_change_in_production_892374928374982374"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    INIT_ADMIN_USERNAME: str = "admin"
    INIT_ADMIN_EMAIL: str = "admin@attendance.com"
    INIT_ADMIN_PASSWORD: str = "AdminPass@123"

    DATABASE_URL_OVERRIDE: str = ""
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """
        Parse comma-separated ALLOWED_ORIGINS string into a list of origins.
        """
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """
        Construct SQLAlchemy MySQL connection URL using PyMySQL driver.
        Supports DATABASE_URL_OVERRIDE for direct cloud DB strings.
        Escapes password to handle special characters cleanly.
        """
        if self.DATABASE_URL_OVERRIDE:
            url = self.DATABASE_URL_OVERRIDE
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url

        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{encoded_password}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
