from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Design, Project, EnvironmentalMetrics, ComplianceResult
from app.schemas import (
    DesignGenerate, 
    DesignGenerateFromSketch, 
    DesignDetailResponse,
    DesignResponse,
    AIReasoningResponse
)
from app.utils.dependencies import get_current_user
from app.services.project_service import ProjectService
from app.ai.generator import get_ai_generator
from app.environmental.analyzer import EnvironmentalAnalyzer
from app.compliance.validator import ComplianceValidator
from PIL import Image
from io import BytesIO
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/design", tags=["Design Generation"])


@router.post("/generate", response_model=DesignDetailResponse, status_code=status.HTTP_201_CREATED)
async def generate_design(
    design_request: DesignGenerate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate architectural design from text prompt"""
    try:
        # Verify project ownership
        project = await ProjectService.get_project_by_id(session, design_request.project_id, current_user.id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Create design record with pending status
        design = Design(
            project_id=design_request.project_id,
            creator_id=current_user.id,
            prompt=design_request.prompt,
            design_type="text-to-design",
            status="processing",
            seed=design_request.seed,
            guidance_scale=design_request.guidance_scale,
            num_inference_steps=design_request.num_inference_steps
        )
        session.add(design)
        await session.flush()
        
        # Generate design
        ai_generator = await get_ai_generator()
        image_path, thumb_path, metadata = await ai_generator.generate_design(
            prompt=design_request.prompt,
            climate_zone=project.climate_zone,
            building_type=project.building_type,
            orientation=project.orientation or 180,
            seed=design_request.seed,
            guidance_scale=design_request.guidance_scale,
            num_inference_steps=design_request.num_inference_steps
        )
        
        # Update design with generated image
        design.image_path = image_path
        design.thumbnail_path = thumb_path
        design.generation_metadata = metadata
        design.status = "completed"
        
        # Generate AI reasoning
        reasoning = ai_generator._generate_design_reasoning(
            design_request.prompt,
            project.climate_zone,
            project.building_type,
            project.orientation or 180
        )
        design.ai_reasoning = reasoning
        
        session.add(design)
        await session.commit()
        await session.refresh(design)
        
        logger.info(f"Design generated: {design.id}")
        return design
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Design generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Design generation failed"
        )


@router.post("/generate-from-sketch", response_model=DesignDetailResponse, status_code=status.HTTP_201_CREATED)
async def generate_from_sketch(
    project_id: int,
    prompt: str,
    sketch_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate architectural design from sketch using ControlNet"""
    try:
        # Verify project ownership
        project = await ProjectService.get_project_by_id(session, project_id, current_user.id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Load sketch image
        sketch_data = await sketch_file.read()
        sketch_image = Image.open(BytesIO(sketch_data)).convert("RGB")
        
        # Create design record
        design = Design(
            project_id=project_id,
            creator_id=current_user.id,
            prompt=prompt,
            design_type="sketch-to-concept",
            status="processing"
        )
        session.add(design)
        await session.flush()
        
        # Generate from sketch
        ai_generator = await get_ai_generator()
        image_path, thumb_path, metadata = await ai_generator.generate_from_sketch(
            sketch_image=sketch_image,
            prompt=prompt
        )
        
        # Update design
        design.image_path = image_path
        design.thumbnail_path = thumb_path
        design.generation_metadata = metadata
        design.status = "completed"
        design.ai_reasoning = ai_generator._generate_design_reasoning(
            prompt,
            project.climate_zone,
            project.building_type,
            project.orientation or 180
        )
        
        session.add(design)
        await session.commit()
        await session.refresh(design)
        
        logger.info(f"Sketch-based design generated: {design.id}")
        return design
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sketch generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sketch-based generation failed"
        )


@router.get("/{design_id}", response_model=DesignDetailResponse)
async def get_design(
    design_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get design details"""
    result = await session.execute(
        select(Design).where(
            (Design.id == design_id) & (Design.creator_id == current_user.id)
        )
    )
    design = result.scalars().first()
    
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Design not found"
        )
    
    return design
