#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from datasets import load_dataset

def main():
    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Script is running from: {os.path.abspath(__file__)}")
    print(f"Output directory: {output_dir}")
    print("Loading dataset from Hugging Face: jonhpark/3kingdoms_qa_ft")
    
    try:
        # Load the dataset from Hugging Face
        dataset = load_dataset("jonhpark/3kingdoms_qa_ft")
        
        # Get all available splits
        splits = dataset.keys()
        print(f"Available splits: {splits}")
        
        # Convert each split to a CSV file
        for split in splits:
            print(f"Processing {split} split...")
            
            # Convert the dataset split to a pandas DataFrame
            df = pd.DataFrame(dataset[split])
            
            # Define the output file path
            output_file = os.path.join(output_dir, f"{split}.csv")
            
            # Save as CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Saved {split} split to {output_file}")
            
            # Display dataset info
            print(f"  - Number of examples: {len(df)}")
            print(f"  - Columns: {', '.join(df.columns)}")
            
        print("\nAll splits have been successfully converted to CSV files!")
    
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 