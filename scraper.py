import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urlparse
from models import Product, BrandInsights

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def safe_get(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch {url} — {e}")
        return None

# 1. Product catalog
def scrape_product_catalog(base_url: str) -> List[Product]:
    if not is_valid_url(base_url):
        return []
    json_url = f"{base_url.rstrip('/')}/products.json"
    res = safe_get(json_url)
    if not res:
        return []
    try:
        data = res.json()
        return [Product(title=p['title'], price=p.get('variants', [{}])[0].get('price'),
                        url=f"{base_url}/products/{p['handle']}") for p in data.get('products', [])]
    except Exception as e:
        print(f"[ERROR] JSON parsing failed for {json_url} — {e}")
        return []

# 2. Hero products
def scrape_hero_products(base_url: str) -> List[Product]:
    res = safe_get(base_url)
    if not res:
        return []
    soup = BeautifulSoup(res.content, 'lxml')
    products = []
    for link in soup.select('a[href*="/products/"]'):
        title = link.text.strip()
        url = link.get('href')
        if title:
            products.append(Product(title=title, url=base_url.rstrip('/') + url, price=None))
    return products

# 3. Policies
def scrape_policy_text(base_url: str, policy_type='privacy') -> str:
    url = f"{base_url.rstrip('/')}/policies/{'privacy-policy' if policy_type == 'privacy' else 'refund-policy'}"
    res = safe_get(url)
    if not res:
        return ""
    soup = BeautifulSoup(res.text, 'lxml')
    return soup.get_text(separator=' ', strip=True)

# 4. FAQs
def scrape_faqs(base_url: str) -> List[str]:
    res = safe_get(base_url)
    if not res:
        return []
    soup = BeautifulSoup(res.content, 'lxml')
    return [el.strip() for el in soup.find_all(string=lambda s: "?" in s and len(s.strip()) > 10)]

# 5. Social handles
def scrape_social_links(base_url: str) -> List[str]:
    res = safe_get(base_url)
    if not res:
        return []
    soup = BeautifulSoup(res.content, 'lxml')
    return [a['href'] for a in soup.find_all('a', href=True) if any(s in a['href'] for s in ['facebook', 'instagram', 'tiktok'])]

# 6. Contact details
def scrape_contact_details(base_url: str) -> List[str]:
    res = safe_get(base_url)
    if not res:
        return []
    soup = BeautifulSoup(res.content, 'lxml')
    text = soup.get_text()
    import re
    emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    phones = re.findall(r'\+?\d[\d\s\-]{8,}\d', text)
    return emails + phones

# 7. About text
def scrape_about_text(base_url: str) -> str:
    url = f"{base_url.rstrip('/')}/pages/about-us"
    res = safe_get(url)
    if not res:
        return ""
    soup = BeautifulSoup(res.text, 'lxml')
    return soup.get_text(separator=' ', strip=True)

# 8. Important links
def scrape_important_links(base_url: str) -> List[str]:
    res = safe_get(base_url)
    if not res:
        return []
    soup = BeautifulSoup(res.content, 'lxml')
    return [a['href'] for a in soup.find_all('a', href=True) if any(k in a['href'].lower() for k in ['order', 'contact', 'blog'])]
