"""
Room Acoustic Simulator Module
Simulates how sound propagates and reflects in a designed room space.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RoomDimensions:
    """Room dimensions in meters."""
    length: float  # x-axis
    width: float   # y-axis
    height: float  # z-axis

@dataclass
class Vector3D:
    """3D vector position."""
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Vector3D') -> float:
        """Calculate distance to another point."""
        return np.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )

class Material:
    """Acoustic material properties."""
    
    # Absorption coefficients for common materials (frequency dependent)
    ABSORPTION_COEFFICIENTS = {
        'drywall': {
            'low': 0.1,
            'mid': 0.05,
            'high': 0.04
        },
        'hardwood': {
            'low': 0.15,
            'mid': 0.11,
            'high': 0.10
        },
        'carpet': {
            'low': 0.2,
            'mid': 0.5,
            'high': 0.6
        },
        'curtain': {
            'low': 0.3,
            'mid': 0.5,
            'high': 0.7
        },
        'concrete': {
            'low': 0.01,
            'mid': 0.015,
            'high': 0.02
        },
        'glass': {
            'low': 0.05,
            'mid': 0.03,
            'high': 0.02
        }
    }
    
    @classmethod
    def get_absorption(cls, material_name: str, freq_range: str = 'mid') -> float:
        """
        Get absorption coefficient for a material.
        
        Args:
            material_name (str): Name of the material.
            freq_range (str): 'low', 'mid', or 'high' frequency range.
            
        Returns:
            float: Absorption coefficient (0-1).
        """
        material_name = material_name.lower()
        if material_name not in cls.ABSORPTION_COEFFICIENTS:
            return 0.1  # Default absorption
        
        return cls.ABSORPTION_COEFFICIENTS[material_name].get(freq_range, 0.1)

class RoomSimulator:
    """Simulates sound behavior in a room."""
    
    def __init__(self, dimensions: RoomDimensions):
        """
        Initialize the RoomSimulator.
        
        Args:
            dimensions (RoomDimensions): Room dimensions.
        """
        self.dimensions = dimensions
        self.materials = {
            'floor': 'hardwood',
            'ceiling': 'drywall',
            'walls': 'drywall'
        }
        self.speaker_pos = Vector3D(x=1, y=1, z=1)
        self.listener_pos = Vector3D(x=2, y=2, z=1.2)
        self.speed_of_sound = 343  # m/s at 20°C
    
    def set_materials(self, materials: Dict[str, str]) -> None:
        """
        Set room materials for acoustic simulation.
        
        Args:
            materials (Dict[str, str]): Dictionary with 'floor', 'ceiling', 'walls'.
        """
        self.materials.update(materials)
    
    def set_speaker_position(self, pos: Vector3D) -> None:
        """Set speaker position in room."""
        self._validate_position(pos)
        self.speaker_pos = pos
    
    def set_listener_position(self, pos: Vector3D) -> None:
        """Set listener position in room."""
        self._validate_position(pos)
        self.listener_pos = pos
    
    def _validate_position(self, pos: Vector3D) -> None:
        """Validate that position is within room bounds."""
        if not (0 <= pos.x <= self.dimensions.length):
            raise ValueError(f"X position {pos.x} outside room length {self.dimensions.length}")
        if not (0 <= pos.y <= self.dimensions.width):
            raise ValueError(f"Y position {pos.y} outside room width {self.dimensions.width}")
        if not (0 <= pos.z <= self.dimensions.height):
            raise ValueError(f"Z position {pos.z} outside room height {self.dimensions.height}")
    
    def calculate_direct_sound(self) -> Dict:
        """
        Calculate direct sound path characteristics.
        
        Returns:
            Dict: Direct sound parameters (distance, delay, amplitude).
        """
        distance = self.speaker_pos.distance_to(self.listener_pos)
        delay = distance / self.speed_of_sound
        
        # Inverse square law: amplitude decreases with distance
        amplitude_factor = 1.0 / (distance ** 2)
        
        return {
            'distance': distance,
            'delay': delay,
            'amplitude_factor': amplitude_factor
        }
    
    def calculate_reverberation_time(self, volume: Optional[float] = None) -> float:
        """
        Calculate room reverberation time (RT60) using Sabine formula.
        RT60 is the time for sound to decay by 60 dB.
        
        Args:
            volume (Optional[float]): Room volume in m³. If None, calculated from dimensions.
            
        Returns:
            float: Reverberation time in seconds.
        """
        if volume is None:
            volume = (self.dimensions.length * 
                     self.dimensions.width * 
                     self.dimensions.height)
        
        # Calculate surface areas
        floor_area = self.dimensions.length * self.dimensions.width
        wall_area = (2 * self.dimensions.length * self.dimensions.height + 
                    2 * self.dimensions.width * self.dimensions.height)
        ceiling_area = self.dimensions.length * self.dimensions.width
        
        # Calculate absorption
        floor_abs = floor_area * Material.get_absorption(self.materials['floor'], 'mid')
        wall_abs = wall_area * Material.get_absorption(self.materials['walls'], 'mid')
        ceiling_abs = ceiling_area * Material.get_absorption(self.materials['ceiling'], 'mid')
        
        total_absorption = floor_abs + wall_abs + ceiling_abs
        
        # Sabine formula: RT60 = 0.161 * V / A
        # where V is volume and A is total absorption
        if total_absorption == 0:
            return float('inf')
        
        rt60 = 0.161 * volume / total_absorption
        return rt60
    
    def calculate_early_reflections(self, max_reflections: int = 5) -> list:
        """
        Calculate early reflections from room surfaces.
        
        Args:
            max_reflections (int): Maximum number of reflections to consider.
            
        Returns:
            list: List of reflection data (distance, delay, amplitude).
        """
        reflections = []
        
        # Define reflection points on walls, floor, ceiling
        reflection_points = [
            # Floor reflections
            Vector3D(self.speaker_pos.x, self.speaker_pos.y, 0),
            # Ceiling reflections
            Vector3D(self.speaker_pos.x, self.speaker_pos.y, self.dimensions.height),
            # Wall reflections (approximate)
            Vector3D(0, self.speaker_pos.y, self.speaker_pos.z),
            Vector3D(self.dimensions.length, self.speaker_pos.y, self.speaker_pos.z),
            Vector3D(self.speaker_pos.x, 0, self.speaker_pos.z),
            Vector3D(self.speaker_pos.x, self.dimensions.width, self.speaker_pos.z),
        ]
        
        for i, ref_point in enumerate(reflection_points[:max_reflections]):
            # Distance from speaker to reflection point to listener
            dist_speaker_to_surface = self.speaker_pos.distance_to(ref_point)
            dist_surface_to_listener = ref_point.distance_to(self.listener_pos)
            total_distance = dist_speaker_to_surface + dist_surface_to_listener
            
            delay = total_distance / self.speed_of_sound
            
            # Amplitude decreases with distance
            amplitude_factor = 1.0 / (total_distance ** 2)
            
            reflections.append({
                'number': i + 1,
                'distance': total_distance,
                'delay': delay,
                'amplitude_factor': amplitude_factor
            })
        
        return sorted(reflections, key=lambda x: x['delay'])
    
    def simulate_frequency_response(self) -> Dict:
        """
        Simulate how the room affects frequency response.
        
        Returns:
            Dict: Frequency response modification by the room.
        """
        direct = self.calculate_direct_sound()
        rt60 = self.calculate_reverberation_time()
        reflections = self.calculate_early_reflections()
        
        return {
            'direct_sound': direct,
            'reverberation_time': rt60,
            'early_reflections': reflections,
            'room_characteristics': {
                'dimensions': {
                    'length': self.dimensions.length,
                    'width': self.dimensions.width,
                    'height': self.dimensions.height
                },
                'materials': self.materials,
                'volume': (self.dimensions.length * 
                          self.dimensions.width * 
                          self.dimensions.height)
            }
        }
    
    def get_room_config(self) -> Dict:
        """Get complete room configuration."""
        return {
            'dimensions': {
                'length': self.dimensions.length,
                'width': self.dimensions.width,
                'height': self.dimensions.height
            },
            'materials': self.materials,
            'speaker_position': {
                'x': self.speaker_pos.x,
                'y': self.speaker_pos.y,
                'z': self.speaker_pos.z
            },
            'listener_position': {
                'x': self.listener_pos.x,
                'y': self.listener_pos.y,
                'z': self.listener_pos.z
            }
        }
