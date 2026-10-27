"""
Administrative Provisioning Script for EventHorizon AI
Securely configures or updates administrator accounts using bcrypt password hashing.
"""
import sys
import os
import argparse
import asyncio
from sqlalchemy import select

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.database import async_session_maker, engine, Base
from backend.app.core.security import hash_password
from backend.app.models.user import User, UserPreference


async def provision_admin(email: str, password: str, full_name: str = "Administrator", role: str = "admin") -> bool:
    """
    Idempotently creates or updates an admin account.
    Never stores plaintext passwords.
    """
    if not email or "@" not in email:
        print(f"[ERROR] Invalid email address: {email}", file=sys.stderr)
        return False

    if not password or len(password) < 8:
        print("[ERROR] Password must be at least 8 characters long.", file=sys.stderr)
        return False

    normalized_email = email.strip().lower()
    hashed = hash_password(password)

    async with async_session_maker() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == normalized_email))
        user = result.scalar_one_or_none()

        if user:
            print(f"[INFO] User {normalized_email} exists (current role: {user.role}). Updating credentials and elevating role...")
            user.hashed_password = hashed
            user.role = role
            user.is_active = True
            user.is_verified = True
            if full_name:
                user.full_name = full_name
        else:
            print(f"[INFO] Creating new {role} user: {normalized_email}...")
            user = User(
                email=normalized_email,
                hashed_password=hashed,
                full_name=full_name,
                role=role,
                is_active=True,
                is_verified=True
            )
            session.add(user)
            await session.flush()

        # Ensure user preference record exists
        pref_res = await session.execute(select(UserPreference).where(UserPreference.user_id == user.id))
        pref = pref_res.scalar_one_or_none()
        if not pref:
            pref = UserPreference(
                user_id=user.id,
                interests='["Hackathons", "AI/ML", "Web3", "Cloud"]',
                preferred_formats='["online", "in_person", "hybrid"]',
                preferred_regions='[]'
            )
            session.add(pref)

        await session.commit()
        print(f"[SUCCESS] Administrator account '{normalized_email}' successfully provisioned with role '{role}'.")
        return True


def main():
    parser = argparse.ArgumentParser(description="Provision an administrator account in EventHorizon AI.")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "harshavardhan.ushakola14@gmail.com"), help="Administrator email")
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "96325481"), help="Administrator initial password")
    parser.add_argument("--name", default=os.getenv("ADMIN_NAME", "Harshavardhan Ushakola"), help="Full name of administrator")
    parser.add_argument("--role", default=os.getenv("ADMIN_ROLE", "admin"), help="Role level (admin or super_admin)")

    args = parser.parse_args()

    success = asyncio.run(provision_admin(
        email=args.email,
        password=args.password,
        full_name=args.name,
        role=args.role
    ))

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
