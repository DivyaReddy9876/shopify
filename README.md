🛍️ Shopify Store Insights-Fetcher Application
📌 Project Overview
This project is a Python + FastAPI backend application that scrapes public data and insights from Shopify-based eCommerce websites, without using the official Shopify API.

It allows users to fetch structured information such as:

Product catalogs

Brand policies (privacy, returns)

FAQs

Contact information

Social media links

Brand context (About Us)

Hero products from homepage

Miscellaneous important links

⚙️ The application is designed using clean architecture, modular code structure, and scalable design principles using FastAPI.

🗂️ Project Structure
graphql
Copy
Edit
shopify_insights/
├── __pycache__/               # Compiled files
├── templates/                 # Optional: HTML rendering if needed
├── venv/                      # Virtual environment
├── app_flask.py               # (Legacy) Flask version - not used now
├── app_fastapi.py             # ✅ FastAPI entry point
├── main.py                    # Main logic trigger (used by FastAPI)
├── scraper.py                 # Shopify site scraping logic
├── competitor_finder.py       # Competitor discovery logic (Bonus)
├── database.py                # DB setup and engine
├── db_ops.py                  # DB interactions (Insert, Fetch)
├── models.py                  # Pydantic models for FastAPI response validation
├── models_db.py               # SQLAlchemy models for database tables
├── shopify.db                 # SQLite DB file (or MySQL)
🚀 Features
✅ Core Features
🔍 Fetch and parse Shopify store using public pages

🛒 Extract Product Catalog via /products.json

🏆 Detect Hero Products from homepage

📃 Get Privacy & Return Policies

❓ Parse FAQs (HTML parsing across common patterns)

🧾 Scrape About Us / Brand Text Context

📱 Fetch Social Media Links (IG, FB, etc.)

📧 Extract Emails, Contact Numbers

🔗 Collect Important Links like blogs, order tracking, contact pages

✅ API exposed via FastAPI

🎁 Bonus Features
🧠 Competitor Brand Identification (Basic scraping logic)

💽 Data Storage in SQLite or MySQL

🔌 API Endpoint
POST /fetch-insights
Request Body:

json
Copy
Edit
{
  "website_url": "https://memy.co.in"
}
Success Response (200 OK):

json
Copy
Edit
{
  "brand_name": "MeMy",
  "products": [...],
  "hero_products": [...],
  "privacy_policy": "...",
  "refund_policy": "...",
  "faqs": [...],
  "about": "...",
  "social_links": {
    "instagram": "https://instagram.com/memy",
    "facebook": "..."
  },
  "contact_details": {
    "emails": ["support@memy.co.in"],
    "phones": ["+91-XXXXXXXXXX"]
  },
  "important_links": {
    "order_tracking": "...",
    "blogs": "...",
    "contact_us": "..."
  }
}
Error Responses:

401 – Website not found or invalid Shopify store

500 – Internal processing/scraping error

⚙️ Setup & Installation
Prerequisites
Python 3.8+

FastAPI

Uvicorn

Optional: MySQL or SQLite

Installation Steps
bash
Copy
Edit
git clone https://github.com/your-repo/shopify_insights.git
cd shopify_insights
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
Run FastAPI Server
bash
Copy
Edit
uvicorn app_fastapi:app --reload
Go to:
http://127.0.0.1:8000/docs → for Swagger UI
http://127.0.0.1:8000/fetch-insights → main POST endpoint

📊 Tech Stack
Language: Python 3.8+

Framework: FastAPI

Scraping: requests, BeautifulSoup, re

Data Models: Pydantic

Database: SQLite (shopify.db) or MySQL (Bonus)

API Docs: OpenAPI/Swagger (via FastAPI)

Runner: Uvicorn

🧪 Testing
bash
Copy
Edit
pytest
Or test endpoints via Postman or Swagger (/docs).

✨ Highlights
Modular Python code with clean architecture

Structured, validated responses using Pydantic

Full error handling with proper HTTP status codes

Optional database integration with SQLAlchemy

Bonus competitor insights logic

📩 Contact
Divya Reddy Seerapu
📧 divyaseerapu7658@gmail.com


<img width="942" height="796" alt="image" src="https://github.com/user-attachments/assets/2134a738-a333-4847-94c6-eaa9b69ea669" />
<img width="708" height="772" alt="image" src="https://github.com/user-attachments/assets/6764701f-8830-4277-9fca-8276ff8a2010" />



