# Dairy Business Management App

A comprehensive Streamlit application for managing a dairy farm business. It tracks expenses, milk sales, cow health/records, and generates reports.

## Features

- **Dashboard:** Overview of daily stats and notifications for recurring expenses or cow events.
- **Expenses:** Track farm expenses with support for recurring payments.
- **Milk Sales:** Record daily milk sales per buyer and manage payments/advances. Supports bulk daily production entry.
- **Cows:** Manage cow records, vaccinations, yield history, and cow-specific expenses.
- **Reports:** Generate and download CSV reports (Daily, Monthly, Buyer Ledgers, Cow Stats).
- **Dual Backend:** Runs completely offline (saving to JSON) OR syncs with Google Sheets.

## Project Structure

```
├── src/
│   ├── app.py                  # Main entry point
│   ├── data_manager.py         # Data abstraction layer & Local Backend
│   ├── google_sheets_backend.py # Google Sheets Backend implementation
│   ├── models.py               # Data classes
│   └── tabs/                   # UI logic for each tab
├── local_data/                 # Stores JSON files when running in Local Mode
├── requirements.txt
└── README.md
```

## How to Run Locally

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App:**
    ```bash
    streamlit run src/app.py
    ```

3.  **Local Mode (Default):**
    - If no credentials are found, the app starts in **Local Mode**.
    - Data is saved in the `local_data/` folder as JSON files.

## How to Enable Google Sheets Backend

To sync data with Google Sheets, you need a Google Cloud Service Account.

1.  **Create Service Account:**
    - Go to Google Cloud Console > IAM & Admin > Service Accounts.
    - Create a new service account.
    - Give it **Editor** access.
    - Create and download a JSON key.

2.  **Configuration:**
    - Rename the downloaded JSON key to `credentials.json`.
    - Place it in the root directory of this project.
    - Restart the app. It will detect the file and switch to "Cloud" mode.

## Deployment to Streamlit Cloud

To publish this app for others to access online:

1.  **Push Code to GitHub:**
    - Ensure your code is in a public or private GitHub repository.
    - **Important:** Do NOT upload your `credentials.json` file to GitHub. Add it to `.gitignore`.

2.  **Deploy on Streamlit Cloud:**
    - Go to [share.streamlit.io](https://share.streamlit.io/) and log in.
    - Click **"New App"**.
    - Select your Repository, Branch, and Main File Path (`src/app.py`).
    - Click **"Deploy"**.

3.  **Configure Secrets (For Google Sheets):**
    - Once deployed, go to your app's **Settings** (three dots in top right > Settings).
    - Go to the **"Secrets"** tab.
    - Paste the content of your `credentials.json` file in the following format:
      ```toml
      [gcp_service_account]
      type = "service_account"
      project_id = "your-project-id"
      private_key_id = "..."
      private_key = "..."
      client_email = "..."
      client_id = "..."
      auth_uri = "..."
      token_uri = "..."
      auth_provider_x509_cert_url = "..."
      client_x509_cert_url = "..."
      ```
      *(You can basically copy the JSON content and paste it under the `[gcp_service_account]` header. Streamlit is smart enough to parse it).*
    - Click **Save**. The app will restart and connect to Google Sheets.

## Troubleshooting

### Error: `APIError: [403]: The user's Drive storage quota has been exceeded`

This error occurs because new Google Cloud Service Accounts often have **0 bytes of storage quota** and cannot create new files.

**Solution:**
1.  **Create the Sheet Manually:** Go to your personal Google Drive and create a blank sheet named **`DairyManagerDB`**.
2.  **Get the Bot Email:** Open your `credentials.json` file and copy the `client_email` address (e.g., `bot@project.iam.gserviceaccount.com`).
3.  **Share the Sheet:** Open your `DairyManagerDB` sheet, click **Share**, paste the bot's email, and give it **Editor** access.
4.  **Restart App:** The app will now connect to this shared sheet instead of trying to create a new one.

## Testing

Run the included unit tests to verify backend logic:
```bash
python -m unittest tests/test_v4.py
```
