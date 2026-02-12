from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Project, Design, EnvironmentalMetrics, ComplianceResult
from app.schemas import AnalyticsSummary, HealthCheckResponse
from app.utils.dependencies import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary for current user"""
    try:
        # Count projects
        projects_result = await session.execute(
            select(func.count(Project.id)).where(Project.user_id == current_user.id)
        )
        total_projects = projects_result.scalar() or 0
        
        # Count designs
        designs_result = await session.execute(
            select(func.count(Design.id)).where(Design.creator_id == current_user.id)
        )
        total_designs = designs_result.scalar() or 0
        
        # Get average sustainability score
        sustainability_result = await session.execute(
            select(func.avg(EnvironmentalMetrics.sustainability_index)).join(
                Design,
                Design.id == EnvironmentalMetrics.design_id
            ).where(
                Design.creator_id == current_user.id
            )
        )
        avg_sustainability = sustainability_result.scalar() or 0
        
        # Get average energy efficiency
        energy_result = await session.execute(
            select(func.avg(EnvironmentalMetrics.energy_efficiency_score)).join(
                Design,
                Design.id == EnvironmentalMetrics.design_id
            ).where(
                Design.creator_id == current_user.id
            )
        )
        avg_energy = energy_result.scalar() or 0
        
        # Get designs by type
        all_designs = await session.execute(
            select(Design).where(Design.creator_id == current_user.id)
        )
        designs = all_designs.scalars().all()
        
        designs_by_type = {}
        designs_by_climate = {}
        
        for design in designs:
            # By type
            design_type = design.design_type or "unknown"
            designs_by_type[design_type] = designs_by_type.get(design_type, 0) + 1
            
            # By climate zone
            climate = design.project.climate_zone if design.project else "unknown"
            designs_by_climate[climate] = designs_by_climate.get(climate, 0) + 1
        
        logger.info(f"Analytics summary generated for user {current_user.id}")
        
        return AnalyticsSummary(
            total_projects=total_projects,
            total_designs_generated=total_designs,
            average_compliance_score=0.0,  # Can be calculated from ComplianceResult
            average_sustainability_index=float(avg_sustainability),
            designs_by_type=designs_by_type,
            designs_by_climate_zone=designs_by_climate
        )
    
    except Exception as e:
        logger.error(f"Analytics summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics summary"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    session: AsyncSession = Depends(get_db)
):
    """Health check endpoint"""
    try:
        # Test database connection
        await session.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        ai_model="ready",
        timestamp=datetime.now()
    )
