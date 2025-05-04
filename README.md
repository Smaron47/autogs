**Automated Scheduler & Google Sheets Integration Web App – Documentation**

---

## Table of Contents

1. Project Overview
2. Key Features
3. Technology Stack & Dependencies
4. Directory & File Structure
5. Environment Setup & Configuration
6. Google Sheets Integration
7. Scheduling Architecture
8. Flask Application Structure

   * 8.1 Helper Functions
   * 8.2 Route Handlers
9. Client-Side Templates Overview
10. Data Flow & JSON Storage
11. Error Handling & Validation
12. Security Considerations
13. Testing & Quality Assurance
14. Deployment & Production Setup
15. SEO Keywords
16. Author & License

---

## 1. Project Overview

This Flask-based web application allows users to schedule periodic data collection tasks for arbitrary URLs and XPaths, storing results in Google Sheets. Users submit a URL, XPath, element index, and execution time; the app schedules jobs via APScheduler and writes scraped or provided data back into a Google Sheets worksheet.

---

## 2. Key Features

* **Dynamic Scheduling:** Run `update_google_sheet()` daily at user-specified times.
* **Google Sheets Sync:** Automatically locate the submitted URL in the sheet and append new column data.
* **CRUD for Tasks:** Add new scraping tasks via form, list existing tasks, download/upload JSON state.
* **RESTful Endpoints:** JSON APIs for retrieving and updating scheduled data.
* **Geolocation (Optional):** Session-based IP lookup for country, if extended.

---

## 3. Technology Stack & Dependencies

* **Python 3.8+**
* **Flask**: Web framework for routes and templates
* **Requests**: For IP geolocation API calls
* **gspread & google-auth**: Google Sheets API client
* **APScheduler**: Background job scheduling
* **Jinja2**: Template rendering

**requirements.txt**:

```
Flask
requests
gspread
google-auth
google-auth-oauthlib
APScheduler
```

---

## 4. Directory & File Structure

```
project_root/
├── app.py                  # Main Flask application
├── templates/
│   ├── index.html          # Task submission form
│   ├── fuck.html           # Debug/demo page
│   └── base.html           # Common layout
├── credet.json             # Google Service Account credentials
├── urls_data.json          # Persisted scheduled tasks
├── static/                 # Optional JS/CSS assets
├── requirements.txt        # Python dependencies
└── README.md               # This documentation
```

---

## 5. Environment Setup & Configuration

1. **Create Python Virtualenv**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
3. **Google Credentials**:

   * Place service account file `credet.json` at project root.
   * Share target Google Sheet with service account email.
4. **Initial JSON File**:

   ```json
   []
   ```

   Save as `urls_data.json` to persist tasks.

---

## 6. Google Sheets Integration

### `init_google()`

* **Scope**: Full access to spreadsheets and Drive
* **Credentials**: Loaded from `credet.json`
* **Worksheet**: Opens by URL and selects worksheet named "WebScrap"

### `append_column(sheet, data, url)`

* Finds the row corresponding to `url` via `sheet.find(url)`
* Determines the next empty column index
* Adds a new column and writes `data` into the cell at (row, new\_col)

---

## 7. Scheduling Architecture

* Uses **BackgroundScheduler** from APScheduler
* On application start: `scheduler.start()`
* When a task is submitted:

  1. Parse `time_str` to `hour` and `minute`.
  2. Create `CronTrigger(hour, minute)` for daily execution.
  3. Schedule `update_google_sheet()` with this trigger.
  4. Store job in `scheduled_jobs` dict keyed by `(url, xpath, index)`.

---

## 8. Flask Application Structure

### 8.1 Helper Functions

* **`datas(s)`**: Safely reads and parses JSON-like files into dict/list; handles trailing comma edge.
* **`lod(e,rea)`**: Normalizes raw JSON string into a dict under key `e`.
* **`wri(fn,da)`**: Writes Python data structure back to file `fn` as JSON string.

### 8.2 Route Handlers

#### `GET/POST /` – `index()`

* **GET**: Renders `index.html` with current server time
* **POST**:

  * Read `url`, `xpath`, `index`, `time_str`
  * Append to `urls_data.json`
  * Insert new row in Google Sheet via `sheet.insert_row()`
  * Schedule daily job and return JSON confirmation

#### `/download_pre_json` (GET)

* Returns current `urls_data` as JSON

#### `/upload_pre_json` (POST)

* Accepts JSON payload `{"url":..., "data":...}`
* Updates matching entry in `urls_data` and writes to disk

#### `/fuck` (GET/POST)

* Renders `fuck.html` (demo route)

---

## 9. Client-Side Templates Overview

* **`index.html`**: Form fields for URL, XPath, element index, time picker. Submits via POST to `/`.
* **`base.html`**: Shared header, footer, and CSS/JS includes.
* **`fuck.html`**: Example/debug template for additional testing.

---

## 10. Data Flow & JSON Storage

1. **User submits** task → `urls_data` list in memory and in `urls_data.json` file
2. **Scheduler fires** → loads `urls_data.json`, calls `update_google_sheet()`
3. **update\_google\_sheet()** reads data array, writes into Google Sheet via `append_column`
4. **Client polls** `/download_pre_json` to fetch live schedule state
5. **Client updates** data values via `/upload_pre_json`

---

## 11. Error Handling & Validation

* **Time Format**: Validated via `datetime.strptime`; returns 400 on error.
* **Google Sheet Not Found**: Catches `CellNotFound` and logs.
* **File I/O**: `datas()` attempts two parsing strategies for robustness.
* **Global Exceptions**: Uncaught exceptions return 500 errors with JSON message.

---

## 12. Security Considerations

* **Service Account File**: Protect `credet.json` from public access.
* **Input Sanitization**: Validate URLs, XPaths, and times before scheduling.
* **Authentication**: Consider adding login to restrict who can schedule jobs.
* **HTTPS**: Serve behind TLS in production.

---

## 13. Testing & Quality Assurance

* **Unit Tests**:

  * `datas()` with well-formed and malformed JSON files.
  * `append_column()` with mock sheet object.
* **Integration Tests**:

  * Form submissions via Flask test client
  * Scheduler invocation and job execution simulation
* **Manual QA**:

  * Verify Google Sheet updates at scheduled times
  * Use `/download_pre_json` and `/upload_pre_json` endpoints

---

## 14. Deployment & Production Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**:

   * `GOOGLE_APPLICATION_CREDENTIALS=credet.json`
3. **Run with Gunicorn**:

   bash
   

gunicorn --bind 0.0.0.0:5000 app\:app

4. **Scheduler Note**: APScheduler runs in-process; use hosted environment that supports background threads.
## 15. SEO Keywords

---
```


Flask scheduler Google Sheets
APScheduler Flask tutorial
dynamic cron jobs Flask
gspread integration
XPath scraper web app
daily data automation

```

---

## 16. Author & License

**Author:** Smaron Biswas  
**Date:** 2025  
**License:** MIT License  

Released under MIT; modify and extend freely.

---

*End of Documentation.*

```
