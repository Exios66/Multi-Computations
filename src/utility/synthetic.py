import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Union, Dict, List, Tuple, Optional
import json
from scipy.signal import savgol_filter
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure testing directory structure exists
def ensure_dir_exists(directory_path: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")

# Create required directories
TESTING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "testing")
PHYSIO_DIR = os.path.join(TESTING_DIR, "physiological")
ensure_dir_exists(TESTING_DIR)
ensure_dir_exists(PHYSIO_DIR)

class ClinicalDataGenerator:
    """Production-grade synthetic clinical data generator with enhanced features"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            'base_time': datetime(2025, 2, 26, 16, 0),
            'duration_hours': 3,
            'resolution_min': 1,
            'signal_ranges': {
                'SpO2': (88, 100),
                'pulse_rate': (60, 140),
                'blood_pressure_sys': (90, 180),
                'resp_rate': (12, 30),
                'temperature': (36.0, 38.5),
                # Eye tracking parameters
                'pupil_diameter_left': (2.0, 8.0),  # mm
                'pupil_diameter_right': (2.0, 8.0),  # mm
                'gaze_x': (-30, 30),  # degrees from center
                'gaze_y': (-20, 20),  # degrees from center
                'blink_rate': (0, 1),  # binary indicator
                'fixation_duration': (50, 500)  # milliseconds
            },
            'event_definitions': {
                'hypoxemia': {
                    'SpO2': {'min': 70, 'max': 90},
                    'pulse_rate': {'delta': +15},
                    'resp_rate': {'delta': +5},
                    'pupil_diameter_left': {'delta': -1.0},
                    'pupil_diameter_right': {'delta': -1.0}
                },
                'tachycardia': {
                    'pulse_rate': {'min': 110, 'max': 140},
                    'blood_pressure_sys': {'delta': +20},
                    'pupil_diameter_left': {'delta': +1.5},
                    'pupil_diameter_right': {'delta': +1.5}
                },
                'fever': {
                    'temperature': {'min': 37.8, 'max': 39.5},
                    'pulse_rate': {'delta': +10},
                    'pupil_diameter_left': {'delta': +0.8},
                    'pupil_diameter_right': {'delta': +0.8}
                },
                'cognitive_load': {
                    'pupil_diameter_left': {'delta': +2.0},
                    'pupil_diameter_right': {'delta': +2.0},
                    'fixation_duration': {'delta': +100},
                    'blink_rate': {'delta': -0.3}
                },
                'fatigue': {
                    'blink_rate': {'delta': +0.5},
                    'pupil_diameter_left': {'delta': -1.2},
                    'pupil_diameter_right': {'delta': -1.2},
                    'fixation_duration': {'delta': -50}
                }
            }
        }
        self.validate_config()
        
    def validate_config(self):
        """Ensure configuration parameters are valid"""
        required_keys = ['base_time', 'duration_hours', 'resolution_min',
                        'signal_ranges', 'event_definitions']
        if not all(key in self.config for key in required_keys):
            raise ValueError("Invalid configuration: missing required parameters")
            
        for param, (low, high) in self.config['signal_ranges'].items():
            if low >= high:
                raise ValueError(f"Invalid range for {param}: {low}-{high}")

    def generate_base_signals(self, num_points: int) -> Dict[str, np.ndarray]:
        """Generate baseline physiological signals with cross-correlation"""
        signals = {}
        sr = self.config['signal_ranges']
        
        # Base vital signs with realistic correlations
        signals['SpO2'] = np.clip(np.random.normal(97.5, 1.0, num_points), *sr['SpO2'])
        signals['pulse_rate'] = np.random.normal(80, 3, num_points)
        signals['blood_pressure_sys'] = 120 + 0.5*(signals['pulse_rate'] - 80) + np.random.normal(0, 3, num_points)
        signals['resp_rate'] = 18 + 0.2*(signals['pulse_rate'] - 80) + np.random.normal(0, 1, num_points)
        signals['temperature'] = np.random.normal(36.8, 0.2, num_points)
        
        # Eye tracking data with realistic patterns
        # Base pupil diameter with correlation to pulse rate
        signals['pupil_diameter_left'] = 4.0 + 0.02*(signals['pulse_rate'] - 80) + np.random.normal(0, 0.3, num_points)
        # Right pupil highly correlated with left but with slight differences
        signals['pupil_diameter_right'] = signals['pupil_diameter_left'] + np.random.normal(0, 0.1, num_points)
        
        # Gaze position (x,y) with realistic scanning patterns
        t = np.linspace(0, 2*np.pi*10, num_points)  # Time vector for oscillations
        signals['gaze_x'] = 5 * np.sin(0.1*t) + 3 * np.sin(0.3*t) + np.random.normal(0, 2, num_points)
        signals['gaze_y'] = 4 * np.cos(0.1*t) + 2 * np.cos(0.2*t) + np.random.normal(0, 2, num_points)
        
        # Blink rate (binary indicator with realistic frequency)
        blink_probability = np.ones(num_points) * 0.05  # Base 5% chance of blink
        # Increase blink probability every 20-30 seconds
        for i in range(0, num_points, np.random.randint(20, 30)):
            if i < num_points:
                blink_probability[i:i+2] = 0.8
        signals['blink_rate'] = (np.random.random(num_points) < blink_probability).astype(float)
        
        # Fixation duration (inversely related to saccade frequency)
        base_fixation = np.ones(num_points) * 200  # Base fixation of 200ms
        for i in range(num_points):
            if signals['blink_rate'][i] > 0.5:  # During blinks
                base_fixation[i] = 0
        signals['fixation_duration'] = base_fixation + np.random.normal(0, 30, num_points)
        
        # Clip all signals to their valid ranges
        for param, values in signals.items():
            if param in sr:
                signals[param] = np.clip(values, *sr[param])
        
        return signals
    
    def apply_clinical_event(self, signals: Dict[str, np.ndarray], event_type: str,
                           start_idx: int, duration: int, intensity: float = 1.0):
        """Apply realistic clinical event patterns to signals"""
        event_config = self.config['event_definitions'].get(event_type)
        if not event_config:
            raise ValueError(f"Unknown event type: {event_type}")
            
        end_idx = min(start_idx + duration, len(signals['SpO2']))
        actual_duration = end_idx - start_idx
        x = np.linspace(0, 1, actual_duration)
        
        for param, rules in event_config.items():
            if param not in signals:
                continue
                
            current_values = signals[param][start_idx:end_idx]
            base_value = np.mean(current_values)
            
            # Apply different effect patterns based on parameter type
            if 'delta' in rules:
                effect = rules['delta'] * intensity * np.sin(np.pi * x)  # Smooth sinusoidal effect
            elif 'min' in rules and 'max' in rules:
                effect = np.linspace(base_value, (rules['min'] + rules['max'])/2, actual_duration)
                effect += np.random.normal(0, (rules['max'] - rules['min'])/10, actual_duration)
            
            # Apply smoothing and clipping
            signals[param][start_idx:end_idx] = np.clip(
                savgol_filter(current_values + effect, 5, 2),
                *self.config['signal_ranges'].get(param, (-np.inf, np.inf))
            )
            
        return signals
    
    def add_sensor_noise(self, signals: Dict[str, np.ndarray], noise_level: float = 0.1):
        """Add realistic sensor noise patterns"""
        for param, values in signals.items():
            if param not in self.config['signal_ranges']:
                continue
                
            # Different noise levels for different parameters
            param_noise = noise_level
            if 'pupil' in param:
                param_noise = noise_level * 0.5  # Less noise for pupil measurements
            elif 'gaze' in param:
                param_noise = noise_level * 2.0  # More noise for gaze position
                
            noise = np.random.normal(0, param_noise * np.std(values), len(values))
            signals[param] = np.clip(values + noise, *self.config['signal_ranges'][param])
        return signals
    
    def generate_dataset(self, events: List[Dict] = None) -> pd.DataFrame:
        """Generate complete dataset with configurable clinical events"""
        num_points = self.config['duration_hours'] * 60 // self.config['resolution_min']
        timestamps = [self.config['base_time'] + timedelta(minutes=i*self.config['resolution_min'])
                     for i in range(num_points)]
        
        signals = self.generate_base_signals(num_points)
        
        # Apply predefined clinical events
        default_events = [
            {'type': 'hypoxemia', 'start': 30, 'duration': 10, 'intensity': 0.8},
            {'type': 'tachycardia', 'start': 65, 'duration': 8, 'intensity': 1.0},
            {'type': 'fever', 'start': 120, 'duration': 15, 'intensity': 0.7},
            {'type': 'cognitive_load', 'start': 45, 'duration': 20, 'intensity': 1.2},
            {'type': 'fatigue', 'start': 100, 'duration': 25, 'intensity': 0.9}
        ]
        
        for event in events or default_events:
            try:
                signals = self.apply_clinical_event(
                    signals, event['type'],
                    event['start'], event['duration'],
                    event.get('intensity', 1.0)
                )
                logger.info(f"Applied {event['type']} event at {event['start']}min")
            except Exception as e:
                logger.error(f"Failed to apply event {event}: {str(e)}")
        
        signals = self.add_sensor_noise(signals)
        
        # Create DataFrame with proper formatting
        df = pd.DataFrame({
            'timestamp': timestamps,
            **{k: np.round(v, 2) if 'pupil' in k or 'gaze' in k or 'fixation' in k 
               else np.round(v, 1) if k != 'pulse_rate' and k != 'blink_rate'
               else v.astype(int)
              for k, v in signals.items()}
        })
        
        # Add metadata
        df.attrs['generation_config'] = json.dumps(self.config, default=str)
        df.attrs['event_log'] = json.dumps(events or default_events)
        
        return df
        
    def visualize_dataset(self, df: pd.DataFrame, output_path: Optional[str] = None):
        """Generate visualizations of the synthetic data"""
        # Create a multi-panel figure
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Synthetic Physiological and Eye Tracking Data', fontsize=16)
        
        # Plot vital signs
        ax1 = axes[0, 0]
        ax1.plot(df['timestamp'], df['SpO2'], 'b-', label='SpO2')
        ax1.set_ylabel('SpO2 (%)')
        ax1.set_title('Oxygen Saturation')
        ax1.grid(True)
        
        ax2 = axes[0, 1]
        ax2.plot(df['timestamp'], df['pulse_rate'], 'r-', label='Pulse')
        ax2.set_ylabel('Pulse Rate (bpm)')
        ax2.set_title('Heart Rate')
        ax2.grid(True)
        
        # Plot eye tracking data
        ax3 = axes[1, 0]
        ax3.plot(df['timestamp'], df['pupil_diameter_left'], 'g-', label='Left Pupil')
        ax3.plot(df['timestamp'], df['pupil_diameter_right'], 'c-', label='Right Pupil')
        ax3.set_ylabel('Diameter (mm)')
        ax3.set_title('Pupil Diameter')
        ax3.legend()
        ax3.grid(True)
        
        ax4 = axes[1, 1]
        ax4.scatter(df['gaze_x'], df['gaze_y'], c=df.index, cmap='viridis', alpha=0.5, s=10)
        ax4.set_xlabel('Horizontal Position (degrees)')
        ax4.set_ylabel('Vertical Position (degrees)')
        ax4.set_title('Gaze Position')
        ax4.grid(True)
        
        ax5 = axes[2, 0]
        ax5.plot(df['timestamp'], df['blink_rate'], 'k-', label='Blinks')
        ax5.set_ylabel('Blink Indicator')
        ax5.set_title('Blink Events')
        ax5.grid(True)
        
        ax6 = axes[2, 1]
        ax6.plot(df['timestamp'], df['fixation_duration'], 'm-', label='Fixation')
        ax6.set_ylabel('Duration (ms)')
        ax6.set_title('Fixation Duration')
        ax6.grid(True)
        
        # Format the figure
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save if output path provided
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved to {output_path}")
            
        return fig

def generate_clinical_data(output_format: str = 'dataframe', save_dir: str = None, **kwargs) -> Union[pd.DataFrame, str, bytes]:
    """
    Generate synthetic clinical data with multiple output format options
    
    Args:
        output_format: One of 'dataframe', 'csv', 'parquet', 'dict', 'json'
        save_dir: Directory to save output files (default: testing/physiological)
        **kwargs: Configuration overrides
        
    Returns:
        Requested format containing synthetic clinical data
    """
    generator = ClinicalDataGenerator(kwargs.get('config'))
    
    try:
        df = generator.generate_dataset(kwargs.get('events'))
        
        # Use the specified directory or default to testing/physiological
        save_dir = save_dir or PHYSIO_DIR
        ensure_dir_exists(save_dir)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"eye_tracking_data_{timestamp}"
        
        # Save data in requested format
        if output_format == 'dataframe':
            # Save a copy to the specified directory
            df.to_csv(os.path.join(save_dir, f"{base_filename}.csv"), index=False)
            df.to_parquet(os.path.join(save_dir, f"{base_filename}.parquet"), index=False)
            
            # Generate and save visualization
            viz_path = os.path.join(save_dir, f"{base_filename}_viz.png")
            generator.visualize_dataset(df, viz_path)
            
            return df
            
        elif output_format == 'csv':
            output_path = os.path.join(save_dir, f"{base_filename}.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"CSV data saved to {output_path}")
            return output_path
            
        elif output_format == 'parquet':
            output_path = os.path.join(save_dir, f"{base_filename}.parquet")
            df.to_parquet(output_path, index=False)
            logger.info(f"Parquet data saved to {output_path}")
            return output_path
            
        elif output_format == 'json':
            output_path = os.path.join(save_dir, f"{base_filename}.json")
            with open(output_path, 'w') as f:
                json.dump(df.to_dict(orient='records'), f, default=str)
            logger.info(f"JSON data saved to {output_path}")
            return output_path
            
        elif output_format == 'dict':
            return df.to_dict(orient='records')
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    except Exception as e:
        logger.error(f"Data generation failed: {str(e)}")
        raise

# Example production usage
if __name__ == "__main__":
    try:
        # Generate data with custom events
        clinical_data = generate_clinical_data(
            output_format='dataframe',
            events=[
                {'type': 'hypoxemia', 'start': 45, 'duration': 15, 'intensity': 0.9},
                {'type': 'tachycardia', 'start': 90, 'duration': 20, 'intensity': 1.2},
                {'type': 'cognitive_load', 'start': 60, 'duration': 30, 'intensity': 1.0},
                {'type': 'fatigue', 'start': 120, 'duration': 40, 'intensity': 0.8}
            ]
        )
        
        logger.info(f"Successfully generated eye tracking and physiological datasets")
        logger.info(f"Data saved to {PHYSIO_DIR}")
        
    except Exception as e:
        logger.critical(f"Critical failure in data generation: {str(e)}")
        raise
