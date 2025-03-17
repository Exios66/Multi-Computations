#!/usr/bin/env python3
"""
Test script for synthetic data generation
"""

import os
import sys
import traceback
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    """Generate synthetic eye tracking data and save to testing/physiological directory"""
    print("Starting synthetic data generation...")
    
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
    
    print(f"Saving data to: {physio_dir}")
    
    # Import the data generator here to avoid import errors
    try:
        print("Importing synthetic data generator...")
        from src.utility.synthetic import generate_clinical_data
        print("Successfully imported synthetic data generator")
    except Exception as e:
        print(f"Error importing synthetic data generator: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
    
    # Generate data with custom events
    try:
        print("Generating clinical data...")
        clinical_data = generate_clinical_data(
            output_format='dataframe',
            save_dir=physio_dir,
            events=[
                {'type': 'hypoxemia', 'start': 45, 'duration': 15, 'intensity': 0.9},
                {'type': 'tachycardia', 'start': 90, 'duration': 20, 'intensity': 1.2},
                {'type': 'cognitive_load', 'start': 60, 'duration': 30, 'intensity': 1.0},
                {'type': 'fatigue', 'start': 120, 'duration': 40, 'intensity': 0.8}
            ]
        )
        
        print(f"Successfully generated eye tracking and physiological datasets")
        print(f"Data shape: {clinical_data.shape}")
        print(f"Data columns: {clinical_data.columns.tolist()}")
        
        # List files in the directory
        print(f"Files in {physio_dir}:")
        if os.path.exists(physio_dir):
            files = os.listdir(physio_dir)
            for file in files:
                file_path = os.path.join(physio_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size} bytes)")
        else:
            print(f"  Directory does not exist: {physio_dir}")
        
    except Exception as e:
        print(f"Error generating data: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 