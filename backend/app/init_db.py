from app.core.database import Base, engine
import app.models


def init_database() -> bool:
    """
    Create all SQLAlchemy tables in the configured database.
    The database itself must already exist.
    """
    try:
        print("Initializing database tables...")

        Base.metadata.create_all(bind=engine)

        print("[SUCCESS] All database tables created successfully.")
        return True

    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    init_database()