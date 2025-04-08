# 3 Kingdoms QA Dataset Manager

This directory contains utilities for managing the 3 Kingdoms QA dataset from Hugging Face.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Download Dataset

To download the dataset from Hugging Face and convert to CSV files:

```
python download_dataset.py
```

This script will:
1. Download the dataset from `jonhpark/3kingdoms_qa_ft` on Hugging Face
2. Process all available splits (train, validation, test, show)
3. Save each split as a separate CSV file in this directory

## Output Files

The script generates the following files:
- `train.csv`: Training dataset
- `validation.csv`: Validation dataset
- `test.csv`: Test dataset
- `show.csv`: Show dataset 