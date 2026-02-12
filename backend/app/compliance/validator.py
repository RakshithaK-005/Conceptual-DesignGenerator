import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ComplianceViolation:
    rule: str
    description: str
    required_value: Any
    actual_value: Any
    severity: str  # critical, warning, info


@dataclass
class ComplianceCheckResult:
    compliance_status: bool
    violations: List[ComplianceViolation]
    min_room_area_compliant: bool
    window_to_wall_compliant: bool
    ventilation_compliant: bool
    orientation_compliant: bool
    floor_space_index_compliant: bool
    setback_compliant: bool
    detailed_report: Dict[str, Any]


class ComplianceValidator:
    """Compliance validation engine for architectural designs"""

    # Compliance thresholds (can be made configurable per region)
    MINIMUM_ROOM_AREA = 10  # square meters
    MINIMUM_WINDOW_TO_WALL_RATIO = 0.15  # 15%
    MINIMUM_VENTILATION_SCORE = 50  # 0-100
    OPTIMAL_ORIENTATIONS = [135, 180, 225]  # South facing (degrees)
    ORIENTATION_TOLERANCE = 30  # degrees
    MAXIMUM_FSI = 3.0  # Floor space index
    MINIMUM_SETBACK = 3.0  # meters

    @staticmethod
    def check_minimum_room_area(
        plot_length: float,
        plot_width: float,
        floor_limit: Optional[int] = None
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if minimum room area requirements are met.
        
        Args:
            plot_length: Length of plot in meters
            plot_width: Width of plot in meters
            floor_limit: Number of floors (optional)
            
        Returns:
            Tuple of (compliant, details)
        """
        plot_area = plot_length * plot_width
        avg_room_area = plot_area / (floor_limit or 1) if floor_limit else plot_area
        avg_room_area_per_floor = avg_room_area / 6  # Assuming ~6 rooms per floor
        
        compliant = avg_room_area_per_floor >= ComplianceValidator.MINIMUM_ROOM_AREA
        
        return compliant, {
            "plot_area": plot_area,
            "avg_room_area": avg_room_area_per_floor,
            "minimum_required": ComplianceValidator.MINIMUM_ROOM_AREA,
            "compliant": compliant
        }

    @staticmethod
    def check_window_to_wall_ratio(window_to_wall_ratio: float) -> tuple[bool, Dict[str, Any]]:
        """Check window-to-wall ratio compliance (15% minimum)"""
        compliant = window_to_wall_ratio >= ComplianceValidator.MINIMUM_WINDOW_TO_WALL_RATIO
        
        return compliant, {
            "ratio": window_to_wall_ratio,
            "minimum_required": ComplianceValidator.MINIMUM_WINDOW_TO_WALL_RATIO,
            "percentage": window_to_wall_ratio * 100,
            "compliant": compliant
        }

    @staticmethod
    def check_ventilation_requirement(ventilation_score: float) -> tuple[bool, Dict[str, Any]]:
        """Check ventilation compliance"""
        compliant = ventilation_score >= ComplianceValidator.MINIMUM_VENTILATION_SCORE
        
        return compliant, {
            "score": ventilation_score,
            "minimum_required": ComplianceValidator.MINIMUM_VENTILATION_SCORE,
            "compliant": compliant
        }

    @staticmethod
    def check_orientation_compliance(orientation: int) -> tuple[bool, Dict[str, Any]]:
        """
        Check if orientation is within acceptable range.
        Optimal is south-facing (180 degrees).
        """
        # Check distance from each optimal orientation
        min_distance = float('inf')
        closest_optimal = None
        
        for optimal in ComplianceValidator.OPTIMAL_ORIENTATIONS:
            distance = min(abs(orientation - optimal), 360 - abs(orientation - optimal))
            if distance < min_distance:
                min_distance = distance
                closest_optimal = optimal
        
        compliant = min_distance <= ComplianceValidator.ORIENTATION_TOLERANCE
        
        return compliant, {
            "orientation": orientation,
            "closest_optimal": closest_optimal,
            "tolerance_degrees": ComplianceValidator.ORIENTATION_TOLERANCE,
            "distance_from_optimal": min_distance,
            "compliant": compliant
        }

    @staticmethod
    def check_floor_space_index(
        plot_area: float,
        total_built_area: float,
        floor_limit: Optional[int] = None
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check floor space index (FSI) compliance.
        FSI = Total built area / Plot area
        """
        if plot_area <= 0:
            return False, {"error": "Invalid plot area"}
        
        fsi = total_built_area / plot_area
        compliant = fsi <= ComplianceValidator.MAXIMUM_FSI
        
        return compliant, {
            "fsi": fsi,
            "maximum_allowed": ComplianceValidator.MAXIMUM_FSI,
            "plot_area": plot_area,
            "total_built_area": total_built_area,
            "compliant": compliant
        }

    @staticmethod
    def check_setback_rules(
        plot_length: float,
        plot_width: float,
        setback_north: float,
        setback_south: float,
        setback_east: float,
        setback_west: float
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check setback compliance.
        Minimum setback from boundaries.
        """
        minimum_setback = ComplianceValidator.MINIMUM_SETBACK
        
        violations = []
        if setback_north < minimum_setback:
            violations.append("North setback insufficient")
        if setback_south < minimum_setback:
            violations.append("South setback insufficient")
        if setback_east < minimum_setback:
            violations.append("East setback insufficient")
        if setback_west < minimum_setback:
            violations.append("West setback insufficient")
        
        compliant = len(violations) == 0
        
        return compliant, {
            "minimum_required": minimum_setback,
            "setbacks": {
                "north": setback_north,
                "south": setback_south,
                "east": setback_east,
                "west": setback_west
            },
            "violations": violations,
            "compliant": compliant
        }

    @staticmethod
    async def validate_design(
        plot_length: float,
        plot_width: float,
        floor_limit: Optional[int],
        window_to_wall_ratio: float,
        ventilation_score: float,
        orientation: int,
        total_built_area: Optional[float] = None,
        setback_north: float = 0,
        setback_south: float = 0,
        setback_east: float = 0,
        setback_west: float = 0
    ) -> ComplianceCheckResult:
        """
        Perform complete compliance check on design.
        
        Returns:
            ComplianceCheckResult with all validation details
        """
        violations: List[ComplianceViolation] = []
        detailed_report = {}
        
        # Check 1: Minimum room area
        room_area_compliant, room_area_details = ComplianceValidator.check_minimum_room_area(
            plot_length, plot_width, floor_limit
        )
        detailed_report["minimum_room_area"] = room_area_details
        
        if not room_area_compliant:
            violations.append(ComplianceViolation(
                rule="MINIMUM_ROOM_AREA",
                description=f"Average room area below minimum ({room_area_details['avg_room_area']:.2f}m² < {room_area_details['minimum_required']}m²)",
                required_value=room_area_details['minimum_required'],
                actual_value=room_area_details['avg_room_area'],
                severity="warning"
            ))
        
        # Check 2: Window-to-wall ratio
        wtw_compliant, wtw_details = ComplianceValidator.check_window_to_wall_ratio(
            window_to_wall_ratio
        )
        detailed_report["window_to_wall_ratio"] = wtw_details
        
        if not wtw_compliant:
            violations.append(ComplianceViolation(
                rule="WINDOW_TO_WALL_RATIO",
                description=f"Window-to-wall ratio below 15% ({wtw_details['percentage']:.1f}%)",
                required_value=f"{ComplianceValidator.MINIMUM_WINDOW_TO_WALL_RATIO * 100}%",
                actual_value=f"{wtw_details['percentage']:.1f}%",
                severity="critical"
            ))
        
        # Check 3: Ventilation
        vent_compliant, vent_details = ComplianceValidator.check_ventilation_requirement(
            ventilation_score
        )
        detailed_report["ventilation"] = vent_details
        
        if not vent_compliant:
            violations.append(ComplianceViolation(
                rule="VENTILATION",
                description=f"Ventilation score below minimum (Score: {ventilation_score:.0f})",
                required_value=ComplianceValidator.MINIMUM_VENTILATION_SCORE,
                actual_value=ventilation_score,
                severity="warning"
            ))
        
        # Check 4: Orientation
        orient_compliant, orient_details = ComplianceValidator.check_orientation_compliance(
            orientation
        )
        detailed_report["orientation"] = orient_details
        
        # Check 5: FSI
        plot_area = plot_length * plot_width
        fsi_compliant = True
        fsi_details = {"compliant": True}
        
        if total_built_area:
            fsi_compliant, fsi_details = ComplianceValidator.check_floor_space_index(
                plot_area, total_built_area, floor_limit
            )
            detailed_report["floor_space_index"] = fsi_details
            
            if not fsi_compliant:
                violations.append(ComplianceViolation(
                    rule="FLOOR_SPACE_INDEX",
                    description=f"FSI exceeds maximum ({fsi_details['fsi']:.2f} > {ComplianceValidator.MAXIMUM_FSI})",
                    required_value=f"<= {ComplianceValidator.MAXIMUM_FSI}",
                    actual_value=f"{fsi_details['fsi']:.2f}",
                    severity="critical"
                ))
        
        # Check 6: Setbacks
        setback_compliant, setback_details = ComplianceValidator.check_setback_rules(
            plot_length, plot_width,
            setback_north, setback_south,
            setback_east, setback_west
        )
        detailed_report["setbacks"] = setback_details
        
        if not setback_compliant:
            for violation_msg in setback_details.get("violations", []):
                violations.append(ComplianceViolation(
                    rule="SETBACK",
                    description=f"{violation_msg} (minimum: {ComplianceValidator.MINIMUM_SETBACK}m)",
                    required_value=f">= {ComplianceValidator.MINIMUM_SETBACK}m",
                    actual_value=f"See violation message",
                    severity="warning"
                ))
        
        # Overall compliance
        overall_compliant = all([
            room_area_compliant,
            wtw_compliant,
            vent_compliant,
            setback_compliant
        ])
        
        # Orientation and FSI are informational
        detailed_report["violations_summary"] = {
            "total_violations": len(violations),
            "critical": sum(1 for v in violations if v.severity == "critical"),
            "warnings": sum(1 for v in violations if v.severity == "warning"),
            "info": sum(1 for v in violations if v.severity == "info")
        }
        
        logger.info(f"Compliance check completed: {overall_compliant}, {len(violations)} violations found")
        
        return ComplianceCheckResult(
            compliance_status=overall_compliant,
            violations=violations,
            min_room_area_compliant=room_area_compliant,
            window_to_wall_compliant=wtw_compliant,
            ventilation_compliant=vent_compliant,
            orientation_compliant=orient_compliant,
            floor_space_index_compliant=fsi_compliant,
            setback_compliant=setback_compliant,
            detailed_report=detailed_report
        )
