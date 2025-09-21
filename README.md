# DealMover Case Study

This project is a simplified workflow to extract financial data (Revenue and Cost of Sales) from 10-K filings and display them in a grid. It consists of a Django backend for PDF parsing and a React frontend for file upload and visualization.

---

## Features

- **Backend (Django)**
  - `/api/extract/` endpoint that accepts:
    - `file` (required, PDF upload)
    - `period_end_date` (optional, `YYYY-MM-DD`)
  - Extracts *Revenue* and *Cost of Sales* from Item 8 → Consolidated Statements of Operations.
  - Normalizes values:
    - Removes `$` symbols and extra spaces.
    - Converts values
  - Returns JSON with the requested values.
  - Handles errors such as unsupported files, missing period, or non-10-K documents.

- **Frontend (React)**
  - Uploads a PDF and optional period end date.
  - Sends request to backend.
  - Displays results in a spreadsheet-like table with:
    - Revenue
    - Gross Profit (Revenue – Cost of Sales)


## Installation

### Clone repo
```bash
   git clone https://github.com/<your-username>/<repo-name>.git
```

### Backend Setup
```bash
cd backend
```
  
```bash
pip install -r requirements.txt
```
Run in terminal
```
python -m spacy download en_core_web_sm
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```
### The backend API 
available at http://127.0.0.1:8000/api/extract/ for uploading PDFs and retrieving extracted financial data.


### Setting Up the React Frontend

Navigate to the frontend folder (if it’s separate):
   ```bash
   cd frontend
   ```
Install dependencies
   ```bash
   npm install

   ```
Start server and load it on the browser
   ```bash
npm start

   ```

### Running Backend Tests

We use `pytest` along with `pytest-django` for testing the Django backend.
Go to the backend directory
```bash
cd backend
```
```bash
 pytest ../tests/tests.py
```

  




