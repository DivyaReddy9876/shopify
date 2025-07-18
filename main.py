from fastapi import FastAPI, HTTPException, Query
from models import BrandInsights
from scraper import *
from database import SessionLocal, engine
from models_db import Base
from db_ops import save_products
from competitor_finder import find_competitors

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Route: Fetch insights and competitors
@app.get("/fetch-insights")
def fetch_insights(website_url: str = Query(..., description="Full Shopify store URL")):
    try:
        if not website_url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid URL")

        # Step 1: Scrape original website
        data = BrandInsights(
            product_catalog=scrape_product_catalog(website_url),
            hero_products=scrape_hero_products(website_url),
            privacy_policy=scrape_policy_text(website_url, "privacy"),
            refund_policy=scrape_policy_text(website_url, "refund"),
            faqs=scrape_faqs(website_url),
            social_handles=scrape_social_links(website_url),
            contact_details=scrape_contact_details(website_url),
            about_text=scrape_about_text(website_url),
            important_links=scrape_important_links(website_url),
        )

        # Step 2: Save main site products to DB
        db = SessionLocal()
        save_products(db, data.product_catalog)
        db.close()

        # Step 3: Find and scrape competitors
        competitors = find_competitors(website_url)
        competitor_data = []

        for comp_url in competitors:
            insights = BrandInsights(
                product_catalog=scrape_product_catalog(comp_url),
                hero_products=scrape_hero_products(comp_url),
                privacy_policy=scrape_policy_text(comp_url, "privacy"),
                refund_policy=scrape_policy_text(comp_url, "refund"),
                faqs=scrape_faqs(comp_url),
                social_handles=scrape_social_links(comp_url),
                contact_details=scrape_contact_details(comp_url),
                about_text=scrape_about_text(comp_url),
                important_links=scrape_important_links(comp_url),
            )
            competitor_data.append({
                "website": comp_url,
                "insights": insights
            })

        # Final combined response
        return {
            "main_brand": website_url,
            "brand_insights": data,
            "competitors_scraped": competitor_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
