# ClickUp to Google Sheets: Real-time Task Tracker & Dashboard

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?logo=fastapi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![ClickUp](https://img.shields.io/badge/ClickUp-7B68EE?logo=clickup&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?logo=google-sheets&logoColor=white)

An automated, real-time ETL (Extract, Transform, Load) pipeline that listens to ClickUp task events via Webhooks and instantly syncs completed tasks to a Google Sheets database. This system also automatically generates and updates a dynamic 30-day performance dashboard, complete with performance charts directly within Google Sheets.

Designed for robust local deployment, the system leverages **Docker** for containerization and **Ngrok** to securely expose the local FastAPI server to the internet, creating a seamless background service.

## ✨ Key Features

- **Real-Time Webhook Integration**: Instantaneous syncing of `taskStatusUpdated` events from ClickUp.
- **Zero-Touch Startup**: Automatically provisions an Ngrok tunnel, cleans up stale ClickUp webhooks, and registers the new endpoint URL upon container startup.
- **Automated Dashboarding**: Dynamically recalculates a 30-day performance summary and orchestrates the Google Sheets API to render an up-to-date Line Chart on the dashboard sheet.
- **Containerized Architecture**: Fully encapsulated in Docker, ensuring consistent environments and eliminating "it works on my machine" issues.
- **Security First**: strict separation of code and configuration. All secrets (API tokens, credentials) are managed via `.env` and external `credentials.json` files.

## 🏗️ Architecture

1. **ClickUp Event Source**: Triggers a webhook payload when a task changes status (e.g., to "Closed").
2. **Ngrok Tunnel**: Routes the external ClickUp HTTP request to the local Docker container.
3. **FastAPI Server**: Validates and extracts the payload, transforming the data into a standard format.
4. **ETL Pipeline**:
   - *Extractor*: Parses task metadata from the ClickUp payload.
   - *Transformer*: Computes rolling 30-day statistics and aggregates performance metrics.
   - *Loader*: Appends raw data to the `Database_Full` sheet and overwrites the `Dashboard_30_Days` sheet, including rendering the chart.

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A ClickUp Workspace and Personal API Token.
- A Google Cloud Service Account with Google Sheets API enabled (`credentials.json`).
- An Ngrok account and Auth Token.

### 1. Configuration & Secrets

Clone the repository and set up your environment variables. Never commit your `.env` or `credentials.json` to version control.

```bash
# Create your environment file
touch .env
```

Edit the `.env` file with your specific credentials. Here is a detailed guide on how to obtain each required variable:

#### 🔑 ClickUp Credentials
- **`CLICKUP_API_TOKEN`**: 
  1. Log in to ClickUp.
  2. Click on your profile avatar (bottom left) -> **Settings** -> **Apps**.
  3. Under **Personal API Token**, click **Generate** (or copy the existing one). It usually starts with `pk_`.
- **`CLICKUP_TEAM_ID`**: 
  1. Open your ClickUp Workspace in the browser.
  2. Look at the URL: `https://app.clickup.com/12345678/v/l/...`
  3. The number right after `clickup.com/` (e.g., `12345678`) is your Team ID (Workspace ID).

#### 📊 Google Sheets Credentials
- **`GOOGLE_SHEET_URL`**: 
  1. Open your target Google Sheet.
  2. Copy the entire URL from the browser's address bar.
- **`GOOGLE_APPLICATION_CREDENTIALS`** (`credentials.json`):
  1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a new Project and enable the **Google Sheets API** and **Google Drive API**.
  3. Go to **IAM & Admin** -> **Service Accounts** -> **Create Service Account**.
  4. Once created, click on the Service Account -> **Keys** -> **Add Key** -> **Create new key** (JSON format).
  5. Rename the downloaded file to `credentials.json` and place it in the root folder of this project.
  6. **Crucial Step**: Open the `credentials.json` file, find the `client_email` address, and **Share** your Google Sheet with this email address (give it Editor permissions).

#### 🌐 Ngrok Credentials
- **`NGROK_AUTHTOKEN`**:
  1. Sign up/Log in at [dashboard.ngrok.com](https://dashboard.ngrok.com).
  2. Go to **Tunnels** -> **Authtokens**.
  3. Copy your Auth Token.

**Your final `.env` file should look exactly like this:**

```ini
CLICKUP_API_TOKEN="pk_12345678_ABCDEFGH..."
CLICKUP_TEAM_ID="12345678"
GOOGLE_SHEET_URL="https://docs.google.com/spreadsheets/d/1abc.../edit"
GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
NGROK_AUTHTOKEN="1abc2def..."
```

### 2. Deployment

Run the system in detached mode using Docker Compose:

```bash
sudo docker compose up -d --build
```

### 3. Verification

Once the container is running:
1. The system will start FastAPI on port 8000.
2. `pyngrok` will expose port 8000 to a public URL.
3. The initialization script will automatically register this new URL with your ClickUp Workspace.
4. Try closing a task in ClickUp—your Google Sheet will be updated instantly!

## 📁 Project Structure

```text
.
├── core/
│   └── config.py          # Pydantic BaseSettings for environment variables
├── etl/
│   ├── extractor.py       # Parses ClickUp webhook payloads
│   ├── transformer.py     # Aggregates data for the 30-day dashboard
│   └── loader.py          # Interfaces with Google Sheets API and charts
├── scripts/
│   ├── register_webhook.py # ClickUp webhook management logic
│   └── start_server.py    # Bootstrapper for Ngrok and Uvicorn
├── webhook_server.py      # FastAPI application entry point
├── docker-compose.yml     # Docker Compose orchestration
├── Dockerfile             # Container image definition
├── requirements.txt       # Python dependencies
└── .env                   # Secrets (Not tracked in Git)
```

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.
