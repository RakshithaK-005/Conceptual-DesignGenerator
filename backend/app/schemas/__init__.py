from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    USER = "user"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


# Authentication Schemas
class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: int
    exp: datetime


# Project Schemas
class PlotConfigurationBase(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    road_direction: Optional[str] = None
    setbacks_north: float = Field(default=0, ge=0)
    setbacks_south: float = Field(default=0, ge=0)
    setbacks_east: float = Field(default=0, ge=0)
    setbacks_west: float = Field(default=0, ge=0)
    floor_limit: Optional[int] = Field(None, gt=0)
    floor_space_index: Optional[float] = Field(None, ge=0)


class PlotConfigurationCreate(PlotConfigurationBase):
    pass


class PlotConfigurationResponse(PlotConfigurationBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    climate_zone: str = Field(..., min_length=1)
    building_type: str = Field(..., min_length=1)
    orientation: Optional[int] = Field(None, ge=0, le=360)


class ProjectCreate(ProjectBase):
    plot_configuration: PlotConfigurationCreate


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    orientation: Optional[int] = None
    climate_zone: Optional[str] = None
    building_type: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    plot_configuration: Optional[PlotConfigurationResponse] = None


# Design Schemas
class AIReasoningResponse(BaseModel):
    design_reasoning: str
    top_influencing_factors: List[str]
    environmental_summary: str
    optimization_suggestions: List[str]


class DesignGenerate(BaseModel):
    project_id: int
    prompt: str = Field(..., min_length=10)
    seed: Optional[int] = None
    guidance_scale: float = Field(default=7.5, ge=1, le=15)
    num_inference_steps: int = Field(default=50, ge=10, le=100)


class DesignGenerateFromSketch(BaseModel):
    project_id: int
    sketch_image_url: str
    prompt: str = Field(..., min_length=10)
    controlnet_conditioning_scale: float = Field(default=1.0, ge=0, le=1)
    seed: Optional[int] = None


class DesignResponse(BaseModel):
    id: int
    project_id: int
    creator_id: int
    prompt: str
    design_type: str
    image_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DesignDetailResponse(DesignResponse):
    ai_reasoning: Optional[AIReasoningResponse] = None
    metadata: Optional[dict] = None


# Environmental Metrics Schemas
class EnvironmentalMetricsResponse(BaseModel):
    id: int
    project_id: int
    design_id: int
    estimated_sunlight_hours: Optional[float] = None
    sun_score: Optional[float] = None
    window_to_wall_ratio: Optional[float] = None
    airflow_score: Optional[float] = None
    orientation_factor: Optional[float] = None
    energy_efficiency_score: Optional[float] = None
    natural_lighting_percentage: Optional[float] = None
    sustainability_index: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EnvironmentalAnalysisRequest(BaseModel):
    project_id: int
    design_id: int
    latitude: float
    orientation: int
    window_ratio: float = Field(..., ge=0, le=1)
    window_to_wall_ratio: float = Field(..., ge=0, le=1)
    climate_zone: str


class SustainabilityIndexResponse(BaseModel):
    sustainability_index: float
    energy_score: float
    natural_lighting_percentage: float
    passive_design_factors: dict
    recommendations: List[str]


# Compliance Schemas
class ComplianceViolation(BaseModel):
    rule: str
    description: str
    required_value: Any
    actual_value: Any
    severity: str  # critical, warning, info


class ComplianceCheckRequest(BaseModel):
    project_id: int
    design_id: int


class ComplianceResultResponse(BaseModel):
    id: int
    project_id: int
    design_id: int
    compliance_status: bool
    violations: List[ComplianceViolation]
    min_room_area_compliant: bool
    window_to_wall_compliant: bool
    ventilation_compliant: bool
    orientation_compliant: bool
    floor_space_index_compliant: bool
    setback_compliant: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsSummary(BaseModel):
    total_projects: int
    total_designs_generated: int
    average_compliance_score: float
    average_sustainability_index: float
    designs_by_type: dict
    designs_by_climate_zone: dict


class HealthCheckResponse(BaseModel):
    status: str
    database: str
    ai_model: str
    timestamp: datetime
