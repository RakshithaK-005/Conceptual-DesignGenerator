from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.utils.auth import hash_password
import logging

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        existing_user = await session.execute(
            select(User).where((User.email == user_data.email) | (User.username == user_data.username))
        )
        if existing_user.scalars().first():
            raise ValueError("User with this email or username already exists")
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"User created: {user.email}")
        return user

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """Get user by email"""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
        """Get user by ID"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def update_user(session: AsyncSession, user: User, update_data: UserUpdate) -> User:
        """Update user profile"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"User updated: {user.email}")
        return user

    @staticmethod
    async def deactivate_user(session: AsyncSession, user: User) -> User:
        """Deactivate user account"""
        user.is_active = False
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"User deactivated: {user.email}")
        return user
