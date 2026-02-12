from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectDetailResponse, ProjectUpdate, ProjectResponse
from app.utils.dependencies import get_current_user
from app.services.project_service import ProjectService
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/create", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new architectural project"""
    try:
        project = await ProjectService.create_project(session, current_user, project_data)
        return project
    except Exception as e:
        logger.error(f"Project creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project = await ProjectService.get_project_by_id(session, project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.get("", response_model=List[ProjectResponse])
async def list_user_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all projects for current user"""
    projects, _ = await ProjectService.get_user_projects(session, current_user.id, skip, limit)
    return projects


@router.put("/{project_id}", response_model=ProjectDetailResponse)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project details"""
    project = await ProjectService.get_project_by_id(session, project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        updated_project = await ProjectService.update_project(session, project, update_data)
        return updated_project
    except Exception as e:
        logger.error(f"Project update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project"""
    project = await ProjectService.get_project_by_id(session, project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    try:
        await ProjectService.delete_project(session, project)
        logger.info(f"Project deleted: {project_id}")
    except Exception as e:
        logger.error(f"Project deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
