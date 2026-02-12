from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Design, Project, EnvironmentalMetrics
from app.schemas import (
    EnvironmentalAnalysisRequest,
    EnvironmentalMetricsResponse,
    SustainabilityIndexResponse
)
from app.utils.dependencies import get_current_user
from app.environmental.analyzer import EnvironmentalAnalyzer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/environment", tags=["Environmental Analysis"])


@router.post("/analyze", response_model=EnvironmentalMetricsResponse, status_code=status.HTTP_201_CREATED)
async def analyze_environmental_metrics(
    analysis_request: EnvironmentalAnalysisRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze environmental metrics for a design"""
    try:
        # Verify design ownership
        result = await session.execute(
            select(Design).where(
                (Design.id == analysis_request.design_id) & 
                (Design.creator_id == current_user.id)
            )
        )
        design = result.scalars().first()
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        # Check if analysis already exists
        existing = await session.execute(
            select(EnvironmentalMetrics).where(
                EnvironmentalMetrics.design_id == analysis_request.design_id
            )
        )
        metrics = existing.scalars().first()
        
        # Perform analysis
        analysis_result = await EnvironmentalAnalyzer.perform_complete_analysis(
            latitude=analysis_request.latitude,
            orientation=analysis_request.orientation,
            window_ratio=analysis_request.window_ratio,
            window_to_wall_ratio=analysis_request.window_to_wall_ratio,
            climate_zone=analysis_request.climate_zone,
            natural_lighting_percentage=80.0,
            cross_ventilation_possible=True,
            passive_design_factors={
                "thermal_mass": True,
                "natural_ventilation": True,
                "solar_shading": True,
                "green_roof": False,
                "rainwater_harvesting": False,
                "material_efficiency": True,
                "cross_ventilation": True
            }
        )
        
        if metrics:
            # Update existing metrics
            metrics.estimated_sunlight_hours = analysis_result.estimated_sunlight_hours
            metrics.sun_score = analysis_result.sun_score
            metrics.window_to_wall_ratio = analysis_result.window_to_wall_ratio
            metrics.airflow_score = analysis_result.airflow_score
            metrics.orientation_factor = analysis_result.orientation_factor
            metrics.energy_efficiency_score = analysis_result.energy_efficiency_score
            metrics.natural_lighting_percentage = analysis_result.natural_lighting_percentage
            metrics.sustainability_index = analysis_result.sustainability_index
            metrics.analysis_details = analysis_result.analysis_details
            metrics.passive_design_factors = analysis_result.passive_design_factors
        else:
            # Create new metrics
            metrics = EnvironmentalMetrics(
                project_id=analysis_request.project_id,
                design_id=analysis_request.design_id,
                estimated_sunlight_hours=analysis_result.estimated_sunlight_hours,
                sun_score=analysis_result.sun_score,
                window_to_wall_ratio=analysis_result.window_to_wall_ratio,
                airflow_score=analysis_result.airflow_score,
                orientation_factor=analysis_result.orientation_factor,
                energy_efficiency_score=analysis_result.energy_efficiency_score,
                natural_lighting_percentage=analysis_result.natural_lighting_percentage,
                sustainability_index=analysis_result.sustainability_index,
                analysis_details=analysis_result.analysis_details,
                passive_design_factors=analysis_result.passive_design_factors
            )
        
        session.add(metrics)
        await session.commit()
        await session.refresh(metrics)
        
        logger.info(f"Environmental analysis completed for design {analysis_request.design_id}")
        return metrics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Environmental analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Environmental analysis failed"
        )


@router.get("/{design_id}/sustainability", response_model=SustainabilityIndexResponse)
async def get_sustainability_index(
    design_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sustainability index for a design"""
    try:
        # Verify design ownership
        result = await session.execute(
            select(Design).where(
                (Design.id == design_id) & 
                (Design.creator_id == current_user.id)
            )
        )
        design = result.scalars().first()
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        # Get environmental metrics
        metrics_result = await session.execute(
            select(EnvironmentalMetrics).where(
                EnvironmentalMetrics.design_id == design_id
            )
        )
        metrics = metrics_result.scalars().first()
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environmental metrics not found. Run analysis first."
            )
        
        return SustainabilityIndexResponse(
            sustainability_index=metrics.sustainability_index,
            energy_score=metrics.energy_efficiency_score,
            natural_lighting_percentage=metrics.natural_lighting_percentage,
            passive_design_factors=metrics.passive_design_factors or {},
            recommendations=metrics.analysis_details.get("recommendations", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sustainability index retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sustainability index"
        )
