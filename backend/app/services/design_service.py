from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Design, Project
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DesignService:
    @staticmethod
    async def create_design(
        session: AsyncSession,
        project_id: int,
        creator_id: int,
        prompt: str,
        design_type: str
    ) -> Design:
        """Create a new design record"""
        design = Design(
            project_id=project_id,
            creator_id=creator_id,
            prompt=prompt,
            design_type=design_type,
            status="pending"
        )
        session.add(design)
        await session.commit()
        await session.refresh(design)
        logger.info(f"Design created: {design.id}")
        return design

    @staticmethod
    async def get_design_by_id(
        session: AsyncSession,
        design_id: int,
        creator_id: Optional[int] = None
    ) -> Design | None:
        """Get design by ID"""
        query = select(Design).where(Design.id == design_id)
        if creator_id:
            query = query.where(Design.creator_id == creator_id)
        
        query = query.options(
            selectinload(Design.project),
            selectinload(Design.environmental_metrics),
            selectinload(Design.compliance_results)
        )
        
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_project_designs(
        session: AsyncSession,
        project_id: int,
        creator_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Design], int]:
        """Get designs for a project"""
        query = select(Design).where(Design.project_id == project_id)
        if creator_id:
            query = query.where(Design.creator_id == creator_id)
        
        query = query.order_by(Design.created_at.desc())
        
        # Get total count
        count_result = await session.execute(
            select(Design).where(Design.project_id == project_id)
        )
        total = len(count_result.scalars().all())
        
        result = await session.execute(query.offset(skip).limit(limit))
        designs = result.scalars().all()
        
        return designs, total

    @staticmethod
    async def update_design_status(
        session: AsyncSession,
        design: Design,
        status: str,
        **kwargs
    ) -> Design:
        """Update design status and optional fields"""
        design.status = status
        
        for key, value in kwargs.items():
            if hasattr(design, key):
                setattr(design, key, value)
        
        session.add(design)
        await session.commit()
        await session.refresh(design)
        logger.info(f"Design updated: {design.id} - Status: {status}")
        return design

    @staticmethod
    async def delete_design(session: AsyncSession, design: Design) -> None:
        """Delete a design"""
        await session.delete(design)
        await session.commit()
        logger.info(f"Design deleted: {design.id}")
