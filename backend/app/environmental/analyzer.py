import math
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentalAnalysisResult:
    sun_score: float
    estimated_sunlight_hours: float
    airflow_score: float
    window_to_wall_ratio: float
    orientation_factor: float
    energy_efficiency_score: float
    natural_lighting_percentage: float
    sustainability_index: float
    analysis_details: Dict[str, Any]
    passive_design_factors: Dict[str, bool]


class EnvironmentalAnalyzer:
    """Environmental analysis engine for architectural designs"""

    # Climate zone configurations
    CLIMATE_CONFIGS = {
        "tropical": {
            "max_sunlight_hours": 10,
            "optimal_window_ratio": 0.20,
            "orientation_preference": "south"
        },
        "temperate": {
            "max_sunlight_hours": 8,
            "optimal_window_ratio": 0.25,
            "orientation_preference": "south"
        },
        "desert": {
            "max_sunlight_hours": 12,
            "optimal_window_ratio": 0.15,
            "orientation_preference": "north"
        },
        "cold": {
            "max_sunlight_hours": 6,
            "optimal_window_ratio": 0.30,
            "orientation_preference": "south"
        }
    }

    @staticmethod
    def calculate_sun_exposure(
        latitude: float,
        orientation: int,
        window_ratio: float,
        climate_zone: str = "temperate"
    ) -> tuple[float, float]:
        """
        Calculate sun exposure score and estimated sunlight hours.
        
        Args:
            latitude: Geographic latitude
            orientation: Building orientation in degrees (0-360)
            window_ratio: Window-to-floor ratio (0-1)
            climate_zone: Climate zone type
            
        Returns:
            Tuple of (sun_score, estimated_sunlight_hours)
        """
        config = EnvironmentalAnalyzer.CLIMATE_CONFIGS.get(
            climate_zone.lower(), 
            EnvironmentalAnalyzer.CLIMATE_CONFIGS["temperate"]
        )
        
        max_sunlight = config["max_sunlight_hours"]
        
        # Calculate latitude factor (closer to equator = more sun)
        latitude_factor = 1.0 - (abs(latitude) / 90.0) * 0.3
        
        # Calculate orientation score (south-facing is optimal in northern hemisphere)
        # Normalize orientation to 0-180 range
        normalized_orientation = min(abs(orientation - 180), 180)
        orientation_bonus = max(0, 1.0 - (normalized_orientation / 180.0))
        orientation_factor = 0.6 + (orientation_bonus * 0.4)
        
        # Window ratio factor
        window_factor = min(window_ratio / config["optimal_window_ratio"], 1.0)
        
        # Combined sun score
        sun_score = (latitude_factor * 0.4 + orientation_factor * 0.4 + window_factor * 0.2) * 100
        sun_score = min(max(sun_score, 0), 100)
        
        # Estimated sunlight hours
        estimated_hours = (sun_score / 100) * max_sunlight
        
        logger.debug(f"Sun exposure calculated: score={sun_score:.2f}, hours={estimated_hours:.2f}")
        return sun_score, estimated_hours

    @staticmethod
    def calculate_ventilation_score(
        window_to_wall_ratio: float,
        cross_ventilation_possible: bool = True
    ) -> float:
        """
        Calculate ventilation score based on window-to-wall ratio.
        
        Args:
            window_to_wall_ratio: Ratio of window area to wall area (0-1)
            cross_ventilation_possible: Whether cross-ventilation is possible
            
        Returns:
            Ventilation score (0-100)
        """
        # WHO/IFC minimum: 15-20% window-to-wall ratio
        min_ratio = 0.15
        optimal_ratio = 0.25
        max_ratio = 0.40
        
        if window_to_wall_ratio < min_ratio:
            score = (window_to_wall_ratio / min_ratio) * 50
        elif window_to_wall_ratio <= optimal_ratio:
            score = 50 + ((window_to_wall_ratio - min_ratio) / (optimal_ratio - min_ratio)) * 30
        else:
            # Beyond optimal, score decreases slightly
            score = 80 - ((window_to_wall_ratio - optimal_ratio) / (max_ratio - optimal_ratio)) * 20
        
        score = min(max(score, 0), 100)
        
        # Bonus for cross-ventilation
        if cross_ventilation_possible:
            score = min(score + 15, 100)
        
        logger.debug(f"Ventilation score calculated: {score:.2f}")
        return score

    @staticmethod
    def calculate_energy_efficiency_score(
        sun_score: float,
        ventilation_score: float,
        orientation_factor: float
    ) -> float:
        """
        Calculate overall energy efficiency score.
        
        Formula:
        EnergyScore = (0.4 * SunScore) + (0.4 * VentilationScore) + (0.2 * OrientationFactor * 100)
        
        Args:
            sun_score: Sun exposure score (0-100)
            ventilation_score: Ventilation score (0-100)
            orientation_factor: Orientation efficiency factor (0-1)
            
        Returns:
            Energy efficiency score (0-100)
        """
        energy_score = (
            (sun_score * 0.4) +
            (ventilation_score * 0.4) +
            (orientation_factor * 100 * 0.2)
        )
        energy_score = min(max(energy_score, 0), 100)
        logger.debug(f"Energy efficiency score: {energy_score:.2f}")
        return energy_score

    @staticmethod
    def calculate_sustainability_index(
        energy_efficiency_score: float,
        natural_lighting_percentage: float,
        passive_design_factors: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive sustainability index.
        
        Args:
            energy_efficiency_score: Energy efficiency score (0-100)
            natural_lighting_percentage: Percentage of naturally lit spaces (0-100)
            passive_design_factors: Dict of passive design implementation status
            
        Returns:
            Dict with sustainability metrics and recommendations
        """
        # Passive design score
        passive_factors = [
            ("thermal_mass", 15),
            ("natural_ventilation", 15),
            ("solar_shading", 12),
            ("green_roof", 10),
            ("rainwater_harvesting", 12),
            ("material_efficiency", 10),
            ("cross_ventilation", 16),
        ]
        
        passive_score = 0
        implemented_count = 0
        details = {}
        
        for factor, weight in passive_factors:
            is_implemented = passive_design_factors.get(factor, False)
            if is_implemented:
                passive_score += weight
                implemented_count += 1
            details[factor] = is_implemented
        
        # Sustainability index combines all factors
        sustainability_index = (
            (energy_efficiency_score * 0.4) +
            (natural_lighting_percentage * 0.3) +
            (passive_score * 0.3)
        )
        sustainability_index = min(max(sustainability_index, 0), 100)
        
        # Generate recommendations
        recommendations = EnvironmentalAnalyzer._generate_recommendations(
            energy_efficiency_score,
            natural_lighting_percentage,
            implemented_count,
            len(passive_factors)
        )
        
        logger.debug(f"Sustainability index calculated: {sustainability_index:.2f}")
        
        return {
            "sustainability_index": sustainability_index,
            "energy_efficiency_score": energy_efficiency_score,
            "natural_lighting_percentage": natural_lighting_percentage,
            "passive_design_score": passive_score,
            "passive_design_detail": details,
            "implemented_features": implemented_count,
            "total_features": len(passive_factors),
            "recommendations": recommendations
        }

    @staticmethod
    def _generate_recommendations(
        energy_score: float,
        lighting_percentage: float,
        implemented_features: int,
        total_features: int
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if energy_score < 60:
            recommendations.append("Improve window-to-wall ratio for better natural ventilation")
            recommendations.append("Optimize building orientation for solar gain")
        elif energy_score < 80:
            recommendations.append("Fine-tune solar shading strategies for year-round comfort")
        
        if lighting_percentage < 70:
            recommendations.append("Increase window size to improve natural lighting")
            recommendations.append("Consider skylights in deep spaces")
        
        if implemented_features < total_features * 0.7:
            recommendations.append(f"Implement more passive design strategies ({total_features - implemented_features} remaining)")
        
        if not recommendations:
            recommendations.append("Design demonstrates excellent sustainability performance")
        
        return recommendations

    @staticmethod
    async def perform_complete_analysis(
        latitude: float,
        orientation: int,
        window_ratio: float,
        window_to_wall_ratio: float,
        climate_zone: str,
        natural_lighting_percentage: float = 80.0,
        cross_ventilation_possible: bool = True,
        passive_design_factors: Dict[str, bool] | None = None
    ) -> EnvironmentalAnalysisResult:
        """
        Perform complete environmental analysis on design.
        
        Args:
            latitude: Geographic latitude
            orientation: Building orientation (0-360 degrees)
            window_ratio: Window-to-floor ratio
            window_to_wall_ratio: Window area to wall area ratio
            climate_zone: Climate zone type
            natural_lighting_percentage: Percentage of naturally lit area
            cross_ventilation_possible: Whether cross-ventilation is viable
            passive_design_factors: Dict of passive design implementations
            
        Returns:
            EnvironmentalAnalysisResult with all metrics
        """
        if passive_design_factors is None:
            passive_design_factors = {}
        
        # Calculate sun exposure
        sun_score, sunlight_hours = EnvironmentalAnalyzer.calculate_sun_exposure(
            latitude, orientation, window_ratio, climate_zone
        )
        
        # Calculate ventilation
        ventilation_score = EnvironmentalAnalyzer.calculate_ventilation_score(
            window_to_wall_ratio, cross_ventilation_possible
        )
        
        # Calculate orientation factor
        normalized_orientation = min(abs(orientation - 180), 180)
        orientation_factor = 1.0 - (normalized_orientation / 180.0)
        
        # Calculate energy efficiency
        energy_score = EnvironmentalAnalyzer.calculate_energy_efficiency_score(
            sun_score, ventilation_score, orientation_factor
        )
        
        # Calculate sustainability
        sustainability_data = EnvironmentalAnalyzer.calculate_sustainability_index(
            energy_score, natural_lighting_percentage, passive_design_factors
        )
        
        return EnvironmentalAnalysisResult(
            sun_score=sun_score,
            estimated_sunlight_hours=sunlight_hours,
            airflow_score=ventilation_score,
            window_to_wall_ratio=window_to_wall_ratio,
            orientation_factor=orientation_factor,
            energy_efficiency_score=energy_score,
            natural_lighting_percentage=natural_lighting_percentage,
            sustainability_index=sustainability_data["sustainability_index"],
            analysis_details=sustainability_data,
            passive_design_factors=sustainability_data.get("passive_design_detail", {})
        )
