"""
Utilities for config and device management.
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: str = "code/config/config.json"):
        """
        Initialize ConfigManager.
        
        Args:
            config_path (str): Path to configuration file.
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {self.config_path}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        default_config = {
            "audio_devices": {},
            "emulation_settings": {
                "source_device": None,
                "target_device": None,
                "auto_normalize": True
            },
            "room_settings": {
                "dimensions": {"length": 5, "width": 4, "height": 3},
                "materials": {"floor": "hardwood", "walls": "drywall", "ceiling": "drywall"},
                "speaker_position": {"x": 1, "y": 1, "z": 1},
                "listener_position": {"x": 2, "y": 2, "z": 1.2}
            },
            "audio_analyzer": {
                "sample_rate": 44100,
                "chunk_size": 1024
            }
        }
        self.save_config(default_config)
        return default_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def save_config(self, config: Optional[Dict] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def add_device(self, device_name: str, profile: Dict) -> None:
        """
        Add an audio device profile.
        
        Args:
            device_name (str): Name of the device.
            profile (Dict): Device profile data.
        """
        if 'audio_devices' not in self.config:
            self.config['audio_devices'] = {}
        
        self.config['audio_devices'][device_name] = profile
        self.save_config()
    
    def get_device(self, device_name: str) -> Optional[Dict]:
        """Get device profile."""
        devices = self.config.get('audio_devices', {})
        return devices.get(device_name)
    
    def list_devices(self) -> list:
        """List all available device names."""
        return list(self.config.get('audio_devices', {}).keys())
