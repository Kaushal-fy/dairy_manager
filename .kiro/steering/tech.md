# Technology Stack

## Framework & Libraries

- **Streamlit**: Main web framework for the UI
- **Pandas**: Data manipulation and CSV report generation
- **gspread**: Google Sheets API integration
- **google-auth**: Google Cloud authentication

## Architecture Pattern

- **Abstract Base Class Pattern**: `DataManager` ABC defines the interface
- **Dual Backend Strategy**: 
  - `LocalJSONBackend`: File-based storage using JSON
  - `GoogleSheetsBackend`: Cloud storage using Google Sheets
- **Dataclass Models**: Type-safe data structures in `models.py`
- **Tab-based UI**: Modular UI components in `src/tabs/`

## Backend Selection Logic

The app automatically selects backend based on credential availability:
1. Streamlit Secrets (for cloud deployment)
2. Local `credentials.json` file
3. Fallback to Local JSON mode

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run src/app.py

# Run tests
python -m unittest tests/test_v4.py
```

### Deployment
- **Streamlit Cloud**: Deploy via GitHub integration
- **Google Sheets Setup**: Requires service account with Editor permissions
- **Secrets Management**: Use TOML format in Streamlit Cloud secrets

## Data Storage

- **Local Mode**: JSON files in `local_data/` directory
- **Cloud Mode**: Google Sheets with predefined worksheet structure
- **Caching**: 5-minute TTL cache for Google Sheets operations with rate limiting
- **Error Handling**: Robust parsing with fallback values for malformed data
- **Data Validation**: Date format validation, UUID detection, and corrupted record skipping
- **API Optimization**: Batch operations and 100ms delays to prevent quota exceeded errors

## Troubleshooting

### Google Sheets API Issues

**Quota Exceeded (429 Error)**:
- Increased cache TTL to 5 minutes
- Added 100ms rate limiting between requests
- Implemented batch operations where possible

**Data Parsing Errors**:
- Added robust error handling for numeric conversions
- Skip empty/malformed rows automatically
- Validate date formats before parsing (reject UUIDs and invalid dates)
- Fallback to default values for missing data
- Skip records with corrupted or misaligned data

**Date Validation**:
- All date fields validated before parsing
- Invalid dates (UUIDs, malformed strings) are skipped
- UI edit operations use try-catch for date parsing with fallback to today's date

**Common Fixes**:
- Ensure Google Sheet headers match expected format
- Verify service account has Editor permissions
- Check for empty rows or misaligned data in sheets
- Delete corrupted rows from Google Sheets if data appears misaligned