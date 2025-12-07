"""
AudioEmm Library Module
Core modules for audio analysis, device equalization, and room simulation.
"""

from .audio import AudioAnalyzer
from .equalizer import DeviceEqualizer
from .room_simulator import RoomSimulator, RoomDimensions, Vector3D, Material
from .utils import ConfigManager

__all__ = [
    'AudioAnalyzer',
    'DeviceEqualizer',
    'RoomSimulator',
    'RoomDimensions',
    'Vector3D',
    'Material',
    'ConfigManager'
]

__version__ = '2.0.0'
