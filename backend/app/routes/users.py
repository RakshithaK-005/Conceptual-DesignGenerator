from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserDetailResponse, UserUpdate
from app.utils.dependencies import get_current_user
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserDetailResponse)
async def update_current_user(
    update_data: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        user = await UserService.update_user(session, current_user, update_data)
        return user
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_account(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate user account"""
    try:
        await UserService.deactivate_user(session, current_user)
        logger.info(f"Account deactivated: {current_user.email}")
    except Exception as e:
        logger.error(f"Deactivation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account"
        )
