# 🏪 Smart Dukaan (स्मार्ट दुकान)
### *Digital Retail Operating System & AI Assistant for Local Shops*

Smart Dukaan is an integrated, cost-effective digital operating system designed for small retail businesses, grocery stores, and local shop owners. It replaces manual paper notebooks and spreadsheets with an automated digital product catalogue, instant POS billing, customer credit (Khata/Udhar) management, sales performance analytics, and a 24/7 AI-powered FAQ assistant grounded on live store inventory using the official **Google Gemini API** (`google-genai` SDK).

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend** | Python 3.13+, Django 5.x | Robust MVC architecture, atomic transactions (`transaction.atomic`) |
| **Database** | MySQL 8.x / SQLite | Relational schema with transactional integrity |
| **Artificial Intelligence** | Google Gemini API | Official `google-genai` Python SDK with dynamic RAG catalog grounding |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive UI, Bootstrap 5, FontAwesome 6, Plus Jakarta Sans |
| **Visual Charts** | Chart.js 4.x | Real-time 7-day revenue trend line & payment split doughnut charts |
| **Authentication** | Django Auth | Role-based store security (Owner / Cashier) |
| **Version Control** | Git & GitHub | Modular architecture with safe `.gitignore` practices |

---

## 🌟 Key Features

### 1. 🛍️ Digital Product Catalogue & Automated Inventory Tracking
- Real-time stock levels with unit conversions (`kg`, `pcs`, `litre`, `packet`, `box`).
- Configurable **low-stock alerts** with visual warning badges to prevent stockouts.
- Automatic audit logging for every purchase, restock, or POS sale (`StockAuditLog`).
- Barcode and SKU search support.

### 2. 🧾 Fast Point of Sale (POS) Billing Terminal
- Touch & scanner-friendly cart interface.
- Instant stock deduction with atomic transactions to eliminate inventory mismatches.
- Multi-mode settlement: **Cash**, **UPI / QR**, and **Khata (Store Credit)**.
- Professional, printable receipts/invoices with custom shop branding.

### 3. 📖 Customer Credit (Khata / Udhar) Management
- Digital Khata ledger for every registered customer.
- Credit limit enforcement to prevent bad debt.
- One-click **WhatsApp payment reminder links** pre-filled with outstanding balance and shop UPI ID.
- Complete chronological statement of credit given vs payments collected.

### 4. 🤖 AI-Powered Shop Assistant ("Dukaan Sahayak")
- Powered by **Google Gemini** (`gemini-2.5-flash`) via the official `google-genai` SDK.
- **Dynamic Context Grounding**: The assistant is automatically briefed with:
  - Current store hours, address, contact, and return policies.
  - Live inventory pricing and real-time stock availability (in stock vs out of stock).
  - Shop FAQs curated by the owner.
- Customer support available in both **English and Hinglish**.

### 5. 📊 Sales Performance & Analytics Dashboard
- Key performance metric cards: Today's sales, Monthly turnover, Total pending Udhar, and Low stock count.
- **Interactive Chart.js Visuals**:
  - 7-Day Revenue Trend Line Chart.
  - Payment Mode Breakdown (Cash vs UPI vs Khata) Doughnut Chart.
  - Top 5 best-selling items ranking.

### 6. 🌐 Public Customer Storefront
- Clean, mobile-responsive showcase where customers can browse inventory, check real-time stock availability, and chat with the AI assistant.

---

## 🚀 Quick Start & Installation Guide

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Git
- MySQL Server (or SQLite for quick local trials)
- Google Gemini API Key ([Get one free from Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/<your-username>/smart-dukaan.git
cd smart-dukaan

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your settings:
```ini
DEBUG=True
SECRET_KEY=your-custom-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost,*

# Database Configuration (MySQL)
DB_ENGINE=mysql
DB_NAME=smart_dukaan_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: To run in lightweight local development mode without MySQL, set `DB_ENGINE=sqlite`)*

### Step 4: Run Migrations & Seed Sample Data
```bash
# Apply database migrations
python manage.py migrate

# Seed sample categories, products, Khata accounts, and admin user
python manage.py seed_data
```

### Step 5: Start the Development Server
```bash
python manage.py runserver
```

Now open your browser:
- **Public Customer Storefront & AI Chat**: `http://127.0.0.1:8000/`
- **Owner Dashboard**: `http://127.0.0.1:8000/dashboard/`
- **POS Billing Terminal**: `http://127.0.0.1:8000/billing/pos/`
- **Khata Book**: `http://127.0.0.1:8000/khata/`
- **Django Admin Portal**: `http://127.0.0.1:8000/admin/`

---

## 🔑 Default Credentials (from Seeder)

- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```

---

## 📂 Project Structure

```
smart-dukaan/
│
├── core/                   # Django project configuration & settings
│   ├── settings.py         # MySQL/SQLite, Gemini API, Auth configs
│   ├── urls.py             # Root URL routing
│   └── views.py            # Storefront public view
│
├── accounts/               # Authentication & user profiles
├── inventory/              # Products, categories, low-stock thresholds, audit logs
├── billing/                # Orders, invoices, atomic checkout API, POS terminal
├── khata/                  # Customer directory, credit ledger, WhatsApp reminders
├── assistant/              # Gemini SDK services, store profile grounding, chat API
├── analytics/              # KPI calculations & Chart.js data endpoints
│
├── static/
│   ├── css/style.css       # Clean dashboard styling & floating AI widget
│   └── js/
│       ├── dashboard_charts.js  # Chart.js visualization logic
│       └── pos.js               # Reactive cart & checkout handler
│
├── templates/              # Modern HTML5 templates
│   ├── base.html           # Master layout with sidebar & top navigation
│   ├── dashboard/          # Analytics & charts
│   ├── billing/            # POS terminal & printable receipts
│   ├── inventory/          # Product catalog & category management
│   ├── khata/              # Customer ledger & credit tracking
│   ├── assistant/          # Store settings, FAQs & AI test playground
│   └── storefront/         # Public customer digital catalogue
│
├── requirements.txt
├── .env.example
├── .gitignore
└── manage.py
```

---

## 📜 License
Developed for local businesses to enable seamless digital retail operations.
