# Chemical Equipment Parameter Visualizer

Hybrid Web + Desktop Application (Django + React + PyQt5)

---

## 📌 Project Overview

This project is a hybrid data visualization and analytics system for chemical equipment datasets.

Users upload a CSV file containing equipment information (Equipment Name, Type, Flowrate, Pressure, Temperature).
The Django backend processes the data using Pandas and exposes REST APIs.

The same backend is consumed by:

* A React.js web application
* A PyQt5 desktop application

Both interfaces display tables, analytics charts, summaries and downloadable reports.

---

## ⚙️ Tech Stack

**Backend**

* Django
* Django REST Framework
* Pandas
* SQLite

**Web Frontend**

* React.js
* Chart.js

**Desktop Frontend**

* PyQt5
* Matplotlib

**Other Features**

* Authentication
* PDF report generation
* Dataset history storage

---

## ✨ Features

* Upload CSV dataset
* Automatic data parsing and validation
* Average Flowrate, Pressure and Temperature calculation
* Equipment type distribution charts
* Data table visualization
* Last 5 dataset history tracking
* PDF report generation
* Login authentication
* Web + Desktop interfaces using same backend API

---

## 🧪 Sample Dataset

A sample file is included:

```
sample_equipment_data.csv
```

Use it for testing.

---

## 🛠 Installation & Setup

### 1️⃣ Run Backend (Django)

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 2️⃣ Run Web Application (React)

Open a new terminal:

```
cd web_frontend
npm install
npm start
```

Web app runs at:

```
http://localhost:3000
```

---

### 3️⃣ Run Desktop Application (PyQt5)

```
cd desktop_frontend
pip install -r requirements.txt
python main.py
```

---

## 🔐 Login

Create a user:

```
python manage.py createsuperuser
```

Then login using those credentials.

---

## 📊 What the Application Demonstrates

* CSV ingestion and data processing
* REST API design
* Hybrid client architecture
* Data visualization
* Desktop + Web integration with a shared backend

---

## 🎥 Demo Video

(Will be added here)
