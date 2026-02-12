import pytest
from fastapi import status


@pytest.mark.asyncio
class TestEnvironmentalAnalysis:
    """Environmental analysis module tests"""

    def test_sun_exposure_calculation(self):
        """Test sun exposure scoring"""
        from app.environmental.analyzer import EnvironmentalAnalyzer
        
        sun_score, sunlight_hours = EnvironmentalAnalyzer.calculate_sun_exposure(
            latitude=19.0,
            orientation=180,
            window_ratio=0.30,
            climate_zone="tropical"
        )
        
        assert 0 <= sun_score <= 100
        assert 0 <= sunlight_hours <= 10

    def test_ventilation_score_low_ratio(self):
        """Test ventilation scoring with low window ratio"""
        from app.environmental.analyzer import EnvironmentalAnalyzer
        
        score = EnvironmentalAnalyzer.calculate_ventilation_score(
            window_to_wall_ratio=0.10
        )
        
        assert 0 <= score <= 100
        assert score < 50  # Below minimum

    def test_ventilation_score_optimal_ratio(self):
        """Test ventilation scoring with optimal ratio"""
        from app.environmental.analyzer import EnvironmentalAnalyzer
        
        score = EnvironmentalAnalyzer.calculate_ventilation_score(
            window_to_wall_ratio=0.25
        )
        
        assert score > 75  # Near optimal

    def test_energy_efficiency_calculation(self):
        """Test energy efficiency score"""
        from app.environmental.analyzer import EnvironmentalAnalyzer
        
        energy_score = EnvironmentalAnalyzer.calculate_energy_efficiency_score(
            sun_score=75,
            ventilation_score=80,
            orientation_factor=0.8
        )
        
        assert 0 <= energy_score <= 100

    def test_sustainability_index(self):
        """Test sustainability index calculation"""
        from app.environmental.analyzer import EnvironmentalAnalyzer
        
        result = EnvironmentalAnalyzer.calculate_sustainability_index(
            energy_efficiency_score=75,
            natural_lighting_percentage=85,
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
        
        assert 0 <= result["sustainability_index"] <= 100
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0


@pytest.mark.asyncio
class TestCompliance:
    """Compliance validation module tests"""

    def test_minimum_room_area_compliance(self):
        """Test minimum room area validation"""
        from app.compliance.validator import ComplianceValidator
        
        compliant, details = ComplianceValidator.check_minimum_room_area(
            plot_length=50,
            plot_width=40,
            floor_limit=5
        )
        
        assert "compliant" in details
        assert "avg_room_area" in details

    def test_window_to_wall_ratio_compliance(self):
        """Test window-to-wall ratio validation"""
        from app.compliance.validator import ComplianceValidator
        
        # Below minimum
        compliant, details = ComplianceValidator.check_window_to_wall_ratio(0.10)
        assert not compliant
        
        # Above minimum
        compliant, details = ComplianceValidator.check_window_to_wall_ratio(0.20)
        assert compliant

    def test_orientation_compliance(self):
        """Test orientation compliance"""
        from app.compliance.validator import ComplianceValidator
        
        # South-facing (optimal)
        compliant, details = ComplianceValidator.check_orientation_compliance(180)
        assert compliant
        
        # Far from optimal
        compliant, details = ComplianceValidator.check_orientation_compliance(0)
        assert not compliant

    def test_setback_compliance(self):
        """Test setback validation"""
        from app.compliance.validator import ComplianceValidator
        
        # Compliant setbacks
        compliant, details = ComplianceValidator.check_setback_rules(
            plot_length=50,
            plot_width=40,
            setback_north=5,
            setback_south=5,
            setback_east=5,
            setback_west=5
        )
        assert compliant
        
        # Non-compliant setbacks
        compliant, details = ComplianceValidator.check_setback_rules(
            plot_length=50,
            plot_width=40,
            setback_north=1,
            setback_south=1,
            setback_east=1,
            setback_west=1
        )
        assert not compliant

    @pytest.mark.asyncio
    async def test_complete_compliance_check(self):
        """Test complete compliance validation"""
        from app.compliance.validator import ComplianceValidator
        
        result = await ComplianceValidator.validate_design(
            plot_length=50,
            plot_width=40,
            floor_limit=5,
            window_to_wall_ratio=0.20,
            ventilation_score=70,
            orientation=180,
            setback_north=5,
            setback_south=5,
            setback_east=5,
            setback_west=5
        )
        
        assert hasattr(result, "compliance_status")
        assert hasattr(result, "violations")
        assert isinstance(result.violations, list)
