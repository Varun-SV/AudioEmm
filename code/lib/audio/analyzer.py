"""
Audio Analyzer Module
Analyzes audio files to extract frequency response and decibel data.
"""

import numpy as np
import librosa
from typing import Tuple, List

class AudioAnalyzer:
    """Analyzes audio files and extracts frequency response characteristics."""
    
    def __init__(self, sr: int = 44100, chunk_size: int = 1024):
        """
        Initialize the AudioAnalyzer.
        
        Args:
            sr (int): Sample rate for analysis.
            chunk_size (int): Size of FFT window.
        """
        self.sr = sr
        self.chunk_size = chunk_size
        if chunk_size % 2 != 0:
            self.chunk_size += 1
    
    def analyze_file(self, audio_file_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Analyze an audio file and extract frequency response.
        
        Args:
            audio_file_path (str): Path to the audio file.
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (frequencies, db_values)
                - frequencies: Array of frequency values
                - db_values: Array of dB magnitudes (averaged across time)
        """
        try:
            y, sr = librosa.load(audio_file_path, sr=self.sr)
        except Exception as e:
            raise ValueError(f"Error loading audio file {audio_file_path}: {e}")
        
        # Calculate frequencies for the FFT window
        frequencies = np.fft.fftfreq(self.chunk_size, 1 / sr)[:self.chunk_size // 2]
        
        db_values = []
        hop_length = self.chunk_size
        
        # Process audio in chunks
        for i in range(0, len(y) - self.chunk_size + 1, hop_length):
            chunk = y[i:i + self.chunk_size]
            
            # Apply Hann window
            window = np.hanning(self.chunk_size)
            windowed_chunk = chunk * window
            
            # FFT and convert to dB
            fft_data = np.abs(np.fft.fft(windowed_chunk))
            fft_data = fft_data[:len(frequencies)]
            
            # Convert to dB (add epsilon to avoid log10(0))
            db = 20 * np.log10(fft_data + 1e-9)
            db_values.append(db)
        
        # Average dB values across time
        db_avg = np.mean(db_values, axis=0) if db_values else np.zeros(len(frequencies))
        
        return frequencies, db_avg
    
    def get_frequency_response_curve(self, audio_file_path: str, smooth: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get a smoothed frequency response curve.
        
        Args:
            audio_file_path (str): Path to the audio file.
            smooth (bool): Whether to apply smoothing.
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (frequencies, smoothed_db_values)
        """
        frequencies, db_values = self.analyze_file(audio_file_path)
        
        if smooth:
            # Apply simple smoothing using moving average
            db_values = self._smooth_array(db_values, window_size=5)
        
        return frequencies, db_values
    
    @staticmethod
    def _smooth_array(arr: np.ndarray, window_size: int = 5) -> np.ndarray:
        """
        Apply moving average smoothing to an array.
        
        Args:
            arr (np.ndarray): Input array.
            window_size (int): Size of the smoothing window.
            
        Returns:
            np.ndarray: Smoothed array.
        """
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(arr, kernel, mode='same')
        return smoothed
    
    @staticmethod
    def normalize_response(db_values: np.ndarray) -> np.ndarray:
        """
        Normalize frequency response to 0 dB reference.
        
        Args:
            db_values (np.ndarray): dB values.
            
        Returns:
            np.ndarray: Normalized dB values.
        """
        max_db = np.max(db_values)
        return db_values - max_db
