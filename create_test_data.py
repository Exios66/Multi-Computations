#!/usr/bin/env python3
"""
Simple script to create testing directories and sample data
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def main():
    """Create testing/physiological directory and sample data file"""
    print("Creating testing directories...")
    
    # Create testing directory structure
    testing_dir = os.path.join(os.path.dirname(__file__), "testing")
    physio_dir = os.path.join(testing_dir, "physiological")
    
    print(f"Creating directory: {testing_dir}")
    if not os.path.exists(testing_dir):
        os.makedirs(testing_dir)
        print(f"Created directory: {testing_dir}")
    else:
        print(f"Directory already exists: {testing_dir}")
    
    print(f"Creating directory: {physio_dir}")
    if not os.path.exists(physio_dir):
        os.makedirs(physio_dir)
        print(f"Created directory: {physio_dir}")
    else:
        print(f"Directory already exists: {physio_dir}")
    
    # Create sample data
    print("Creating sample eye tracking data...")
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"eye_tracking_data_{timestamp}"
    
    # Create a simple DataFrame with eye tracking data
    num_points = 180
    base_time = datetime(2025, 2, 26, 16, 0)
    timestamps = [base_time + timedelta(minutes=i) for i in range(num_points)]
    
    # Generate sample data
    np.random.seed(42)  # For reproducibility
    data = {
        'timestamp': timestamps,
        'SpO2': np.clip(np.random.normal(97.5, 1.0, num_points), 88, 100),
        'pulse_rate': np.random.normal(80, 3, num_points).astype(int),
        'blood_pressure_sys': np.clip(np.random.normal(120, 10, num_points), 90, 180),
        'resp_rate': np.clip(np.random.normal(18, 2, num_points), 12, 30),
        'temperature': np.clip(np.random.normal(36.8, 0.2, num_points), 36.0, 38.5),
        'pupil_diameter_left': np.clip(np.random.normal(4.0, 0.5, num_points), 2.0, 8.0),
        'pupil_diameter_right': np.clip(np.random.normal(4.0, 0.5, num_points), 2.0, 8.0),
        'gaze_x': np.random.normal(0, 10, num_points),
        'gaze_y': np.random.normal(0, 8, num_points),
        'blink_rate': np.random.binomial(1, 0.05, num_points),
        'fixation_duration': np.clip(np.random.normal(200, 50, num_points), 50, 500)
    }
    
    df = pd.DataFrame(data)
    
    # Save data in multiple formats
    csv_path = os.path.join(physio_dir, f"{base_filename}.csv")
    parquet_path = os.path.join(physio_dir, f"{base_filename}.parquet")
    
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV data to: {csv_path}")
    
    df.to_parquet(parquet_path, index=False)
    print(f"Saved Parquet data to: {parquet_path}")
    
    # List files in the directory
    print(f"Files in {physio_dir}:")
    files = os.listdir(physio_dir)
    for file in files:
        file_path = os.path.join(physio_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"  - {file} ({file_size} bytes)")

if __name__ == "__main__":
    main() 