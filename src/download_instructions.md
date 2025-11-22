# Flight Data 2024 - Dataset Download Instructions

## Dataset Information
- **Source**: Kaggle - Flight Data 2024
- **URL**: https://www.kaggle.com/datasets/hrishitpatil/flight-data-2024
- **Expected Size**: ~7+ million rows (potentially up to 50M+ rows)
- **Format**: CSV file(s)
- **Scope**: U.S. domestic flight data for 2024

## Prerequisites
1. **Kaggle Account**: You must have a registered Kaggle account
2. **Kaggle API Token** (Optional but recommended for automation):
   - Go to your Kaggle account settings
   - Scroll to "API" section
   - Click "Create New API Token"
   - This downloads `kaggle.json` to your computer

## Manual Download Instructions

### Step 1: Access the Dataset
1. Navigate to: https://www.kaggle.com/datasets/hrishitpatil/flight-data-2024
2. Log in to your Kaggle account if not already logged in
3. Click the **"Download"** button in the top-right corner of the dataset page

### Step 2: Download the Files
1. Kaggle will download a ZIP file containing the dataset
2. Expected file name: `flight-data-2024.zip` or similar
3. Note the download location on your computer

### Step 3: Extract and Move Files
1. Extract the ZIP file contents
2. You should see one or more CSV files (e.g., `flights_2024.csv` or similar)
3. **Move all CSV files** to the following directory in this project:
   ```
   /home/user/Flight-delay/data/raw/
   ```

### Step 4: Verify File Placement
After moving the files, your directory structure should look like:
```
Flight-delay/
├── data/
│   ├── raw/
│   │   └── [your_dataset_file.csv]  # One or more CSV files here
│   └── processed/  # Will be populated after running ingestion notebook
├── notebooks/
├── src/
└── reports/
```

## Alternative: Kaggle API Download (Advanced)

If you have Kaggle API set up, you can download directly:

```bash
# Install Kaggle API
pip install kaggle

# Place your kaggle.json in ~/.kaggle/
mkdir -p ~/.kaggle
cp /path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download the dataset
cd /home/user/Flight-delay/data/raw/
kaggle datasets download -d hrishitpatil/flight-data-2024

# Extract the downloaded ZIP file
unzip flight-data-2024.zip
rm flight-data-2024.zip  # Optional: remove ZIP after extraction
```

## Verification Checklist

Before proceeding to data ingestion, verify:

- [ ] CSV file(s) are located in `data/raw/` directory
- [ ] File size is reasonable (should be several GB for 7M+ rows)
- [ ] File can be opened in a text editor (check first few lines)
- [ ] File contains header row with column names
- [ ] No corruption warnings when opening the file

## Expected File Size Guidelines

- **7 million rows**: Approximately 1-3 GB (depending on number of columns)
- **50+ million rows**: Approximately 5-15 GB or more
- If file size seems unusually small, verify download completed successfully

## Column Expectations

The dataset should contain flight-related columns such as:
- Flight identifiers (flight number, tail number)
- Temporal data (date, scheduled/actual departure/arrival times)
- Geographic data (origin/destination airports)
- Delay metrics (departure delay, arrival delay)
- Carrier/airline information
- Cancellation/diversion indicators

## Troubleshooting

### Issue: Download fails or times out
- **Solution**: Try downloading during off-peak hours or use Kaggle API

### Issue: ZIP extraction fails
- **Solution**: Verify ZIP file integrity, try different extraction tool

### Issue: CSV file is corrupted
- **Solution**: Re-download the dataset, check internet connection stability

### Issue: Access denied to Kaggle dataset
- **Solution**: Ensure you're logged in and have accepted dataset terms

## Next Steps

Once files are in `data/raw/`:
1. Open and run `notebooks/data_ingestion_cleaning.ipynb`
2. The notebook will automatically detect files in `data/raw/`
3. Follow the notebook execution to complete data ingestion and cleaning

## Data Usage Note

This dataset is provided for educational and case study purposes. Please review and comply with:
- Kaggle's Terms of Service
- Dataset-specific usage terms on the Kaggle page
- Your university's academic integrity policies

---

**Last Updated**: 2025-11-22
**Project Phase**: Phase 1 - Data Ingestion & Preparation
