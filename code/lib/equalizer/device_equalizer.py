"""
Device Equalizer Module
Handles device emulation by calculating equalization curves based on frequency response differences.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from ..audio import AudioAnalyzer

class DeviceEqualizer:
    """Creates equalizers to emulate one audio device using another."""
    
    def __init__(self):
        """Initialize the DeviceEqualizer."""
        self.analyzer = AudioAnalyzer()
        self.source_profile = None
        self.target_profile = None
        self.eq_curve = None
    
    def load_device_profile(self, audio_file_path: str, device_name: str) -> Dict:
        """
        Load and analyze a device profile from an audio file.
        
        Args:
            audio_file_path (str): Path to a reference audio file.
            device_name (str): Name of the device being profiled.
            
        Returns:
            Dict: Device profile with frequencies and dB values.
        """
        frequencies, db_values = self.analyzer.get_frequency_response_curve(
            audio_file_path, 
            smooth=True
        )
        
        # Normalize to 0 dB reference
        normalized_db = self.analyzer.normalize_response(db_values)
        
        profile = {
            'name': device_name,
            'frequencies': frequencies,
            'db_values': normalized_db,
            'file_path': audio_file_path
        }
        
        return profile
    
    def set_source_device(self, audio_file_path: str, device_name: str) -> None:
        """
        Set the source device (the device you're using).
        
        Args:
            audio_file_path (str): Path to reference audio from source device.
            device_name (str): Name of the source device.
        """
        self.source_profile = self.load_device_profile(audio_file_path, device_name)
    
    def set_target_device(self, audio_file_path: str, device_name: str) -> None:
        """
        Set the target device (the device you want to emulate).
        
        Args:
            audio_file_path (str): Path to reference audio from target device.
            device_name (str): Name of the target device.
        """
        self.target_profile = self.load_device_profile(audio_file_path, device_name)
    
    def calculate_eq_curve(self) -> Optional[np.ndarray]:
        """
        Calculate the equalization curve to emulate the target device using the source device.
        
        The EQ curve is the difference: target_response - source_response
        
        Returns:
            Optional[np.ndarray]: EQ curve in dB, or None if devices not properly set.
        """
        if self.source_profile is None or self.target_profile is None:
            raise ValueError("Both source and target devices must be set before calculating EQ curve.")
        
        # Ensure both profiles have the same frequency resolution
        source_freqs = self.source_profile['frequencies']
        target_freqs = self.target_profile['frequencies']
        
        if len(source_freqs) != len(target_freqs):
            # Interpolate to match frequencies
            source_db = np.interp(
                target_freqs, 
                source_freqs, 
                self.source_profile['db_values']
            )
            target_db = self.target_profile['db_values']
        else:
            source_db = self.source_profile['db_values']
            target_db = self.target_profile['db_values']
        
        # Calculate EQ curve: what needs to be applied to source to match target
        self.eq_curve = target_db - source_db
        
        return self.eq_curve
    
    def get_eq_curve(self) -> Optional[np.ndarray]:
        """
        Get the current equalization curve.
        
        Returns:
            Optional[np.ndarray]: The EQ curve, or None if not calculated.
        """
        return self.eq_curve
    
    def apply_eq_to_audio(self, audio_signal: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply the equalization curve to an audio signal.
        
        Args:
            audio_signal (np.ndarray): Input audio signal.
            sr (int): Sample rate.
            
        Returns:
            np.ndarray: Equalized audio signal.
        """
        if self.eq_curve is None:
            raise ValueError("EQ curve must be calculated before applying to audio.")
        
        # Perform STFT
        D = np.abs(np.fft.rfft(audio_signal))
        freqs = np.fft.rfftfreq(len(audio_signal), 1/sr)
        
        # Interpolate EQ curve to match FFT frequency bins
        target_freqs = self.target_profile['frequencies']
        eq_curve_interp = np.interp(freqs, target_freqs, self.eq_curve)
        
        # Convert dB to linear gain
        gain_linear = 10 ** (eq_curve_interp / 20)
        
        # Apply gain to magnitude spectrum
        D_eq = D * gain_linear
        
        # Reconstruct audio (simple approach, preserves phase)
        audio_eq = np.fft.irfft(D_eq, n=len(audio_signal))
        
        return audio_eq
    
    def get_device_comparison(self) -> Dict:
        """
        Get a comparison of source and target device characteristics.
        
        Returns:
            Dict: Comparison data for visualization.
        """
        if self.source_profile is None or self.target_profile is None:
            raise ValueError("Both devices must be set for comparison.")
        
        return {
            'source_name': self.source_profile['name'],
            'target_name': self.target_profile['name'],
            'source_frequencies': self.source_profile['frequencies'],
            'source_db': self.source_profile['db_values'],
            'target_frequencies': self.target_profile['frequencies'],
            'target_db': self.target_profile['db_values'],
            'eq_curve': self.eq_curve
        }
