from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Design, Project, PlotConfiguration, ComplianceResult
from app.schemas import ComplianceCheckRequest, ComplianceResultResponse
from app.utils.dependencies import get_current_user
from app.compliance.validator import ComplianceValidator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["Compliance Validation"])


@router.post("/check", response_model=ComplianceResultResponse, status_code=status.HTTP_201_CREATED)
async def check_compliance(
    compliance_request: ComplianceCheckRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check architectural compliance for a design"""
    try:
        # Verify design ownership
        result = await session.execute(
            select(Design).where(
                (Design.id == compliance_request.design_id) & 
                (Design.creator_id == current_user.id)
            )
        )
        design = result.scalars().first()
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        # Get project and plot configuration
        project_result = await session.execute(
            select(Project).where(Project.id == compliance_request.project_id)
        )
        project = project_result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        plot_result = await session.execute(
            select(PlotConfiguration).where(
                PlotConfiguration.project_id == compliance_request.project_id
            )
        )
        plot_config = plot_result.scalars().first()
        
        if not plot_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plot configuration not found"
            )
        
        # Perform compliance validation
        compliance_result = await ComplianceValidator.validate_design(
            plot_length=plot_config.length,
            plot_width=plot_config.width,
            floor_limit=plot_config.floor_limit,
            window_to_wall_ratio=0.20,  # Default value, should come from design analysis
            ventilation_score=70,  # Default value, should come from environmental analysis
            orientation=project.orientation or 180,
            total_built_area=None,
            setback_north=plot_config.setbacks_north,
            setback_south=plot_config.setbacks_south,
            setback_east=plot_config.setbacks_east,
            setback_west=plot_config.setbacks_west
        )
        
        # Check if compliance result already exists
        existing = await session.execute(
            select(ComplianceResult).where(
                ComplianceResult.design_id == compliance_request.design_id
            )
        )
        existing_result = existing.scalars().first()
        
        if existing_result:
            # Update existing
            existing_result.compliance_status = compliance_result.compliance_status
            existing_result.violations = [
                {
                    "rule": v.rule,
                    "description": v.description,
                    "required_value": v.required_value,
                    "actual_value": v.actual_value,
                    "severity": v.severity
                }
                for v in compliance_result.violations
            ]
            existing_result.min_room_area_compliant = compliance_result.min_room_area_compliant
            existing_result.window_to_wall_compliant = compliance_result.window_to_wall_compliant
            existing_result.ventilation_compliant = compliance_result.ventilation_compliant
            existing_result.orientation_compliant = compliance_result.orientation_compliant
            existing_result.floor_space_index_compliant = compliance_result.floor_space_index_compliant
            existing_result.setback_compliant = compliance_result.setback_compliant
            existing_result.compliance_details = compliance_result.detailed_report
            compliance_db_result = existing_result
        else:
            # Create new
            compliance_db_result = ComplianceResult(
                project_id=compliance_request.project_id,
                design_id=compliance_request.design_id,
                compliance_status=compliance_result.compliance_status,
                violations=[
                    {
                        "rule": v.rule,
                        "description": v.description,
                        "required_value": v.required_value,
                        "actual_value": v.actual_value,
                        "severity": v.severity
                    }
                    for v in compliance_result.violations
                ],
                min_room_area_compliant=compliance_result.min_room_area_compliant,
                window_to_wall_compliant=compliance_result.window_to_wall_compliant,
                ventilation_compliant=compliance_result.ventilation_compliant,
                orientation_compliant=compliance_result.orientation_compliant,
                floor_space_index_compliant=compliance_result.floor_space_index_compliant,
                setback_compliant=compliance_result.setback_compliant,
                compliance_details=compliance_result.detailed_report
            )
        
        session.add(compliance_db_result)
        await session.commit()
        await session.refresh(compliance_db_result)
        
        logger.info(f"Compliance check completed for design {compliance_request.design_id}: {compliance_db_result.compliance_status}")
        return compliance_db_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compliance check failed"
        )


@router.get("/{design_id}/status", response_model=ComplianceResultResponse)
async def get_compliance_status(
    design_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance status for a design"""
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
        
        compliance_result = await session.execute(
            select(ComplianceResult).where(
                ComplianceResult.design_id == design_id
            )
        )
        compliance = compliance_result.scalars().first()
        
        if not compliance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compliance result not found. Run compliance check first."
            )
        
        return compliance
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compliance status retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status"
        )
