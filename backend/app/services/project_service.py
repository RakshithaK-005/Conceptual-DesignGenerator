from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Project, PlotConfiguration, User
from app.schemas import ProjectCreate, ProjectUpdate
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ProjectService:
    @staticmethod
    async def create_project(
        session: AsyncSession, 
        user: User, 
        project_data: ProjectCreate
    ) -> Project:
        """Create a new project with plot configuration"""
        project = Project(
            user_id=user.id,
            name=project_data.name,
            description=project_data.description,
            latitude=project_data.latitude,
            longitude=project_data.longitude,
            climate_zone=project_data.climate_zone,
            building_type=project_data.building_type,
            orientation=project_data.orientation,
        )
        
        session.add(project)
        await session.flush()
        
        # Create plot configuration
        plot_config = PlotConfiguration(
            project_id=project.id,
            length=project_data.plot_configuration.length,
            width=project_data.plot_configuration.width,
            road_direction=project_data.plot_configuration.road_direction,
            setbacks_north=project_data.plot_configuration.setbacks_north,
            setbacks_south=project_data.plot_configuration.setbacks_south,
            setbacks_east=project_data.plot_configuration.setbacks_east,
            setbacks_west=project_data.plot_configuration.setbacks_west,
            floor_limit=project_data.plot_configuration.floor_limit,
            floor_space_index=project_data.plot_configuration.floor_space_index,
        )
        session.add(plot_config)
        await session.commit()
        await session.refresh(project)
        
        logger.info(f"Project created: {project.id} by user {user.id}")
        return project

    @staticmethod
    async def get_project_by_id(
        session: AsyncSession, 
        project_id: int, 
        user_id: Optional[int] = None
    ) -> Project | None:
        """Get project by ID"""
        query = select(Project).where(Project.id == project_id)
        if user_id:
            query = query.where(Project.user_id == user_id)
        
        query = query.options(selectinload(Project.plot_configuration))
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_user_projects(
        session: AsyncSession, 
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """Get all projects for a user"""
        query = select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        
        # Get total count
        count_result = await session.execute(select(Project).where(Project.user_id == user_id))
        total = len(count_result.scalars().all())
        
        result = await session.execute(query.offset(skip).limit(limit))
        projects = result.scalars().all()
        
        return projects, total

    @staticmethod
    async def update_project(
        session: AsyncSession, 
        project: Project, 
        update_data: ProjectUpdate
    ) -> Project:
        """Update project details"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)
        
        session.add(project)
        await session.commit()
        await session.refresh(project)
        logger.info(f"Project updated: {project.id}")
        return project

    @staticmethod
    async def delete_project(session: AsyncSession, project: Project) -> None:
        """Delete project"""
        await session.delete(project)
        await session.commit()
        logger.info(f"Project deleted: {project.id}")

    @staticmethod
    async def update_plot_configuration(
        session: AsyncSession,
        project_id: int,
        plot_data: dict
    ) -> PlotConfiguration:
        """Update plot configuration"""
        result = await session.execute(
            select(PlotConfiguration).where(PlotConfiguration.project_id == project_id)
        )
        plot_config = result.scalars().first()
        
        if not plot_config:
            raise ValueError("Plot configuration not found")
        
        for key, value in plot_data.items():
            if hasattr(plot_config, key):
                setattr(plot_config, key, value)
        
        session.add(plot_config)
        await session.commit()
        await session.refresh(plot_config)
        logger.info(f"Plot configuration updated for project {project_id}")
        return plot_config
