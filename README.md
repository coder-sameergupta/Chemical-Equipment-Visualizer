# Chemical Equipment Parameter Visualizer

A hybrid application (Web + Desktop) for analyzing and visualizing chemical equipment data.

## Features
- **Centralized Backend**: Django + REST Framework.
- **Web Frontend**: React + Chart.js (Modern Dark UI).
- **Desktop Frontend**: PyQt5 + Matplotlib.
- **Analytics**: CSV Upload, Automatic Summary Statistics, Data Visualization.
- **Reporting**: PDF Report Generation.

## Prerequisites
- Python 3.10+
- Node.js & npm

## Setup & Running

### 1. Backend (Django)
The backend manages the database and API.

```bash
cd backend
# Create virtual environment (if not exists)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install PyQt5 requests  # For Desktop App

# Migrations
python manage.py makemigrations
python manage.py migrate

# Run Server
python manage.py runserver
```
API will be available at `http://localhost:8000/api/`.

### 2. Web Application (React)
```bash
cd web_frontend
npm install
npm run dev
```
Open `http://localhost:5173`. Login with any credentials (Mock Auth).

### 3. Desktop Application (PyQt5)
```bash
cd desktop_frontend
# Ensure backend venv is activated or installed in your environment
..\backend\venv\Scripts\python main.py
```

## Usage
1.  **Upload**: Use `sample_equipment_data.csv` provided in the root.
2.  **Analyze**: View Dashboard for charts and stats.
3.  **Report**: Click "Download PDF Report" on Web or Desktop.

Backend: Added equipment database models
Backend: Implemented CSV upload functionality
Backend: Added Pandas CSV parsing and preprocessing
Backend: Calculated average flowrate, pressure and temperature
Backend: Implemented equipment type distribution analysis
Backend: Created REST API endpoints using Django REST Framework
Backend: Added user authentication system
Backend: Implemented PDF report generation
