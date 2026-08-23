import sys
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole


def create_initial_admin() -> None:
    """
    Safely seeds or creates the initial ADMIN user account for development.
    Reads credentials from environment settings (INIT_ADMIN_USERNAME, INIT_ADMIN_EMAIL, INIT_ADMIN_PASSWORD).
    Prevents duplicate admin user creation.
    """
    db = SessionLocal()
    try:
        username = settings.INIT_ADMIN_USERNAME
        email = settings.INIT_ADMIN_EMAIL
        password = settings.INIT_ADMIN_PASSWORD

        # Check if an admin account already exists
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"[NOTICE] Admin account already exists (Username: '{existing_admin.username}', Email: '{existing_admin.email}'). Skipping creation.")
            return

        # Check if username or email is taken by another role
        user_by_name = db.query(User).filter(User.username == username).first()
        user_by_email = db.query(User).filter(User.email == email).first()

        if user_by_name or user_by_email:
            print(f"[NOTICE] A user with username '{username}' or email '{email}' already exists. Skipping creation.")
            return

        # Create new initial admin account
        hashed_pwd = hash_password(password)
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_pwd,
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("[SUCCESS] Initial Admin account created successfully!")
        print(f"  - User ID: {admin_user.id}")
        print(f"  - Username: {admin_user.username}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Role: {admin_user.role.value}")
        print("  - Password: [CONFIGURED IN .ENV (INIT_ADMIN_PASSWORD)]")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to create initial admin account: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()
