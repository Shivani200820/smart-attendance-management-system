import pymysql
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # Ensure all SQLAlchemy models are registered with Base.metadata


def init_database() -> bool:
    """
    Attempts to connect to MySQL host, creates database if missing,
    and initializes all application tables safely without dropping existing data.
    """
    print(f"Connecting to MySQL server at {settings.DB_HOST}:{settings.DB_PORT} as user '{settings.DB_USER}'...")
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            autocommit=True
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}`;")
            print(f"[SUCCESS] Database '{settings.DB_NAME}' created or verified successfully.")
        connection.close()

        # Create tables using SQLAlchemy metadata
        print("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All database models initialized successfully.")
        return True

    except Exception as e:
        err_msg = str(e)
        if settings.DB_PASSWORD and settings.DB_PASSWORD in err_msg:
            err_msg = err_msg.replace(settings.DB_PASSWORD, "****")
        print(f"[NOTICE] Database initialization returned: {err_msg}")
        print(f"[ACTION REQUIRED] Ensure your local MySQL server is running and configuration in .env is correct.")
        return False


if __name__ == "__main__":
    init_database()

