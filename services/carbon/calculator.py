"""
Carbon footprint calculation service.
Implements GHG Protocol and SBTi-compliant emission calculations.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TransportMode(str, Enum):
    """Transportation modes with emission factors."""
    CAR_PETROL = "car_petrol"
    CAR_DIESEL = "car_diesel"
    CAR_ELECTRIC = "car_electric"
    BUS = "bus"
    TRAIN = "train"
    FLIGHT_DOMESTIC = "flight_domestic"
    FLIGHT_INTERNATIONAL = "flight_international"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    WALKING = "walking"


@dataclass
class EmissionFactor:
    """Emission factor data for transport modes."""
    mode: TransportMode
    kg_co2_per_km: float
    description: str


# GHG Protocol compliant emission factors (kg CO2e per km per passenger)
EMISSION_FACTORS: Dict[TransportMode, EmissionFactor] = {
    TransportMode.CAR_PETROL: EmissionFactor(
        mode=TransportMode.CAR_PETROL,
        kg_co2_per_km=0.192,
        description="Petrol car (average, per passenger)"
    ),
    TransportMode.CAR_DIESEL: EmissionFactor(
        mode=TransportMode.CAR_DIESEL,
        kg_co2_per_km=0.171,
        description="Diesel car (average, per passenger)"
    ),
    TransportMode.CAR_ELECTRIC: EmissionFactor(
        mode=TransportMode.CAR_ELECTRIC,
        kg_co2_per_km=0.053,
        description="Electric car (India grid mix, per passenger)"
    ),
    TransportMode.BUS: EmissionFactor(
        mode=TransportMode.BUS,
        kg_co2_per_km=0.089,
        description="Bus (average occupancy, per passenger)"
    ),
    TransportMode.TRAIN: EmissionFactor(
        mode=TransportMode.TRAIN,
        kg_co2_per_km=0.041,
        description="Train (diesel/electric mix, per passenger)"
    ),
    TransportMode.FLIGHT_DOMESTIC: EmissionFactor(
        mode=TransportMode.FLIGHT_DOMESTIC,
        kg_co2_per_km=0.255,
        description="Domestic flight (economy class, per passenger)"
    ),
    TransportMode.FLIGHT_INTERNATIONAL: EmissionFactor(
        mode=TransportMode.FLIGHT_INTERNATIONAL,
        kg_co2_per_km=0.195,
        description="International flight (economy class, per passenger)"
    ),
    TransportMode.MOTORCYCLE: EmissionFactor(
        mode=TransportMode.MOTORCYCLE,
        kg_co2_per_km=0.113,
        description="Motorcycle (average, per passenger)"
    ),
    TransportMode.BICYCLE: EmissionFactor(
        mode=TransportMode.BICYCLE,
        kg_co2_per_km=0.0,
        description="Bicycle (zero emissions)"
    ),
    TransportMode.WALKING: EmissionFactor(
        mode=TransportMode.WALKING,
        kg_co2_per_km=0.0,
        description="Walking (zero emissions)"
    ),
}


@dataclass
class CarbonCalculationResult:
    """Result of carbon footprint calculation."""
    distance_km: float
    transport_mode: TransportMode
    emission_factor: float
    total_emissions_kg: float
    total_emissions_tonnes: float
    equivalent_trees: float  # Trees needed to offset for 1 year
    description: str


class CarbonCalculator:
    """Calculator for travel carbon footprint."""
    
    # Average CO2 absorption by one tree per year (kg)
    TREE_CO2_ABSORPTION_KG_PER_YEAR = 21.0
    
    def __init__(self, default_emission_factor: float = 0.12):
        """
        Initialize carbon calculator.
        
        Args:
            default_emission_factor: Default emission factor if mode not found
        """
        self.default_emission_factor = default_emission_factor
    
    def calculate(
        self,
        distance_km: float,
        transport_mode: TransportMode,
        passengers: int = 1
    ) -> CarbonCalculationResult:
        """
        Calculate carbon emissions for a journey.
        
        Args:
            distance_km: Distance traveled in kilometers
            transport_mode: Mode of transportation
            passengers: Number of passengers (for shared transport)
            
        Returns:
            CarbonCalculationResult with emission details
        """
        if distance_km <= 0:
            raise ValueError("Distance must be positive")
        
        if passengers <= 0:
            raise ValueError("Number of passengers must be positive")
        
        # Get emission factor
        emission_data = EMISSION_FACTORS.get(transport_mode)
        
        if emission_data is None:
            logger.warning(
                f"Unknown transport mode: {transport_mode}, "
                f"using default factor: {self.default_emission_factor}"
            )
            emission_factor = self.default_emission_factor
            description = f"Unknown mode (default factor: {emission_factor} kg CO2/km)"
        else:
            emission_factor = emission_data.kg_co2_per_km
            description = emission_data.description
        
        # Calculate total emissions
        total_emissions_kg = distance_km * emission_factor * passengers
        total_emissions_tonnes = total_emissions_kg / 1000.0
        
        # Calculate tree equivalents
        equivalent_trees = total_emissions_kg / self.TREE_CO2_ABSORPTION_KG_PER_YEAR
        
        result = CarbonCalculationResult(
            distance_km=distance_km,
            transport_mode=transport_mode,
            emission_factor=emission_factor,
            total_emissions_kg=total_emissions_kg,
            total_emissions_tonnes=total_emissions_tonnes,
            equivalent_trees=equivalent_trees,
            description=description
        )
        
        logger.info(
            f"Calculated emissions: {total_emissions_kg:.2f} kg CO2e "
            f"for {distance_km:.1f} km via {transport_mode}"
        )
        
        return result
    
    def compare_modes(
        self,
        distance_km: float,
        modes: Optional[list[TransportMode]] = None
    ) -> Dict[TransportMode, CarbonCalculationResult]:
        """
        Compare emissions across different transport modes.
        
        Args:
            distance_km: Distance to compare
            modes: List of modes to compare (default: all)
            
        Returns:
            Dictionary mapping modes to their emission results
        """
        if modes is None:
            modes = list(TransportMode)
        
        results = {}
        for mode in modes:
            try:
                results[mode] = self.calculate(distance_km, mode)
            except Exception as e:
                logger.error(f"Failed to calculate for {mode}: {e}")
        
        return results
    
    def get_green_alternatives(
        self,
        distance_km: float,
        current_mode: TransportMode,
        max_alternatives: int = 3
    ) -> list[tuple[TransportMode, CarbonCalculationResult, float]]:
        """
        Get greener transportation alternatives.
        
        Args:
            distance_km: Distance to travel
            current_mode: Current transportation mode
            max_alternatives: Maximum number of alternatives to return
            
        Returns:
            List of (mode, result, savings_percentage) tuples, sorted by emissions
        """
        current_result = self.calculate(distance_km, current_mode)
        current_emissions = current_result.total_emissions_kg
        
        # Calculate all modes
        all_results = self.compare_modes(distance_km)
        
        # Filter greener alternatives
        alternatives = []
        for mode, result in all_results.items():
            if mode != current_mode and result.total_emissions_kg < current_emissions:
                savings_pct = (
                    (current_emissions - result.total_emissions_kg) / current_emissions * 100
                )
                alternatives.append((mode, result, savings_pct))
        
        # Sort by emissions (lowest first)
        alternatives.sort(key=lambda x: x[1].total_emissions_kg)
        
        return alternatives[:max_alternatives]
    
    @staticmethod
    def get_available_modes() -> list[TransportMode]:
        """Get list of all available transport modes."""
        return list(TransportMode)
    
    @staticmethod
    def get_emission_factor(mode: TransportMode) -> Optional[float]:
        """Get emission factor for a specific mode."""
        emission_data = EMISSION_FACTORS.get(mode)
        return emission_data.kg_co2_per_km if emission_data else None
