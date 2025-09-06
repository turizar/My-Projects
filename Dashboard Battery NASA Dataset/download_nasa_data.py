#!/usr/bin/env python3
"""
NASA Battery Dataset Downloader - Simple Version
Downloads data to current directory
"""

import kagglehub
import shutil
from pathlib import Path

def main():
    print("🔋 NASA Battery Dataset Downloader")
    
    # Check if data already exists
    if Path("cleaned_dataset_battery_NASA/metadata.csv").exists():
        print("✅ Data already exists!")
        return
    
    print("📥 Downloading NASA battery dataset...")
    try:
        # Download dataset
        kaggle_path = kagglehub.dataset_download("patrickfleith/nasa-battery-dataset")
        
        # Copy to current directory
        shutil.copytree(kaggle_path, "cleaned_dataset_battery_NASA")
        
        # Fix nested structure if needed
        nested_dir = Path("cleaned_dataset_battery_NASA/cleaned_dataset")
        if nested_dir.exists():
            print("📁 Fixing directory structure...")
            for item in nested_dir.iterdir():
                shutil.move(str(item), "cleaned_dataset_battery_NASA/")
            nested_dir.rmdir()
        
        print("✅ Dataset downloaded and organized!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
