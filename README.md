🛍️ Shopify Store Insights Fetcher
A high-performance Python + FastAPI backend application designed to extract deep insights and public data from any Shopify-based eCommerce store—without requiring the official Shopify API.

Using advanced web scraping and pattern matching, this tool generates structured JSON profiles for brands, covering everything from product catalogs to legal policies and social media footprints.

🚀 Key Features
🔍 Data Extraction Capabilities
Product Intelligence: Fetches full catalogs via /products.json and identifies "Hero Products" directly from the homepage.

Legal & Brand Compliance: Automatically scrapes Privacy Policies, Return Policies, and "About Us" brand narratives.

Knowledge Base Parsing: Extracts and structures FAQs using custom HTML pattern detection.

Lead Generation & Social: Scrapes contact emails, phone numbers, and social media links (Instagram, Facebook, etc.).

Navigation Mapping: Collects essential links for order tracking, blogs, and contact pages.

🧠 Advanced Functionality
Competitor Discovery: Basic logic to identify similar brand profiles.

Data Persistence: Integrated SQLAlchemy support for SQLite or MySQL storage.

FastAPI Powered: Fully documented via Swagger UI with strict Pydantic validation for all responses.

📊 Tech Stack
Language: Python 3.8+

Framework: FastAPI

Scraping Engine: requests, BeautifulSoup4, re (Regex)

Data Validation: Pydantic

Database: SQLite / MySQL (SQLAlchemy ORM)

Server: Uvicorn

🗂️ Project Structure
GraphQL
shopify_insights/
├── app_fastapi.py      # ✅ FastAPI entry point & API routes
├── main.py             # Logic orchestrator
├── scraper.py          # Shopify-specific scraping engine
├── models.py           # Pydantic models (API Validation)
├── models_db.py        # SQLAlchemy models (Database Schema)
├── database.py         # DB connection & engine setup
├── db_ops.py           # CRUD operations (Insert/Fetch)
├── competitor_finder.py # Competitor discovery logic
└── shopify.db          # Local SQLite storage
⚙️ Installation & Setup
Clone the Repository

Bash
git clone https://github.com/your-repo/shopify_insights.git
cd shopify_insights
Environment Setup

Bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Run the Server

Bash
uvicorn app_fastapi:app --reload
🔌 API Usage
Endpoint: POST /fetch-insights
Request Body:

JSON
{
  "website_url": "https://memy.co.in"
}
Success Response (200 OK):
Provides a comprehensive JSON object including brand_name, products, hero_products, policies, faqs, social_links, and contact_details.

🎥 Demos & Documentation
Interactive API Docs: http://127.0.0.1:8000/docs

Full Application Video Demo: Watch Video

FastAPI Request Demo: Watch Demo

Database Retrieval Preview: View Database Operations

