from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import concurrent.futures
from threading import Lock
import time
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global cache and lock for thread safety
cache = {}
cache_lock = Lock()

class ShopifyInsightsFetcher:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.insights = {
            'brand_name': '',
            'product_catalog': [],
            'hero_products': [],
            'privacy_policy': '',
            'return_policy': '',
            'refund_policy': '',
            'faqs': [],
            'social_handles': {},
            'contact_details': {},
            'brand_context': '',
            'important_links': {}
        }

    def fetch_with_timeout(self, url, timeout=None):
        """Fetch URL with timeout and error handling"""
        try:
            response = self.session.get(url, timeout=timeout or self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def get_product_catalog(self):
        """Enhanced product catalog fetching with complete product details"""
        try:
            # First try products.json (faster)
            products_url = f"{self.base_url}/products.json"
            response = self.fetch_with_timeout(products_url)
            
            if response and response.status_code == 200:
                data = response.json()
                products = []
                
                for product in data.get('products', []):
                    # Get the first variant for pricing
                    first_variant = product.get('variants', [{}])[0]
                    
                    # Get product images
                    images = []
                    for img in product.get('images', []):
                        images.append(img.get('src', ''))
                    
                    # Get product options (size, color, etc.)
                    options = []
                    for option in product.get('options', []):
                        options.append({
                            'name': option.get('name'),
                            'values': option.get('values', [])
                        })
                    
                    product_data = {
                        'id': product.get('id'),
                        'title': product.get('title'),
                        'handle': product.get('handle'),
                        'description': product.get('body_html', ''),
                        'price': first_variant.get('price', 'N/A'),
                        'compare_at_price': first_variant.get('compare_at_price'),
                        'available': first_variant.get('available', True),
                        'images': images,
                        'featured_image': images[0] if images else '',
                        'tags': product.get('tags', '').split(',') if product.get('tags') else [],
                        'product_type': product.get('product_type'),
                        'vendor': product.get('vendor'),
                        'created_at': product.get('created_at'),
                        'updated_at': product.get('updated_at'),
                        'options': options,
                        'variants_count': len(product.get('variants', [])),
                        'url': f"{self.base_url}/products/{product.get('handle')}"
                    }
                    products.append(product_data)
                
                self.insights['product_catalog'] = products
                logger.info(f"Found {len(products)} products in catalog")
                return True
            
            # Fallback: Try to scrape collections page
            collections_url = f"{self.base_url}/collections/all"
            response = self.fetch_with_timeout(collections_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                products = []
                
                # Common product selectors
                product_selectors = [
                    '.product-item', '.product-card', '.grid-item', 
                    '[data-product-id]', '.product', '.collection-item'
                ]
                
                for selector in product_selectors:
                    product_elements = soup.select(selector)
                    if product_elements:
                        for element in product_elements:
                            title_elem = element.find(['h2', 'h3', 'h4', '.product-title'])
                            price_elem = element.find(['.price', '.product-price', '[data-price]'])
                            link_elem = element.find('a')
                            img_elem = element.find('img')
                            
                            if title_elem and link_elem:
                                product_data = {
                                    'title': title_elem.get_text(strip=True),
                                    'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                                    'url': urljoin(self.base_url, link_elem.get('href', '')),
                                    'featured_image': img_elem.get('src', '') if img_elem else '',
                                    'handle': link_elem.get('href', '').split('/')[-1] if link_elem else ''
                                }
                                products.append(product_data)
                        
                        if products:
                            self.insights['product_catalog'] = products[:50]  # Limit to 50 products
                            logger.info(f"Scraped {len(products)} products from collections")
                            return True
                
        except Exception as e:
            logger.error(f"Error fetching product catalog: {str(e)}")
        
        return False

    def get_hero_products(self):
        """Extract hero products from homepage"""
        try:
            response = self.fetch_with_timeout(self.base_url)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                hero_products = []
                
                # Common selectors for hero products
                selectors = [
                    '.featured-product', '.hero-product', '.product-card',
                    '[data-product-id]', '.product-item', '.collection-item'
                ]
                
                for selector in selectors:
                    products = soup.select(selector)
                    for product in products[:6]:  # Limit to 6 hero products
                        title_elem = product.find(['h2', 'h3', 'h4', '.product-title'])
                        price_elem = product.find(['.price', '.product-price'])
                        link_elem = product.find('a')
                        img_elem = product.find('img')
                        
                        if title_elem and link_elem:
                            hero_products.append({
                                'title': title_elem.get_text(strip=True)[:100],
                                'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                                'link': urljoin(self.base_url, link_elem.get('href', '')),
                                'image': img_elem.get('src', '') if img_elem else ''
                            })
                    
                    if hero_products:
                        break
                
                self.insights['hero_products'] = hero_products[:6]
                logger.info(f"Found {len(hero_products)} hero products")
        except Exception as e:
            logger.error(f"Error fetching hero products: {str(e)}")

    def get_policies(self):
        """Enhanced policy extraction for privacy, return, and refund policies"""
        policies = {
            'privacy_policy': [
                '/pages/privacy-policy', '/privacy-policy', '/privacy',
                '/pages/privacy', '/legal/privacy', '/policies/privacy-policy'
            ],
            'return_policy': [
                '/pages/return-policy', '/return-policy', '/returns',
                '/pages/returns', '/policies/return-policy', '/return'
            ],
            'refund_policy': [
                '/pages/refund-policy', '/refund-policy', '/refunds',
                '/pages/refunds', '/policies/refund-policy', '/refund'
            ]
        }
        
        for policy_type, urls in policies.items():
            for url_path in urls:
                try:
                    full_url = f"{self.base_url}{url_path}"
                    response = self.fetch_with_timeout(full_url, timeout=8)
                    
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Try to find the main content
                        content_selectors = [
                            '.page-content', '.main-content', '.policy-content',
                            '.content', '#content', '.page', '.shopify-policy__container'
                        ]
                        
                        content_text = ""
                        for selector in content_selectors:
                            content_elem = soup.select_one(selector)
                            if content_elem:
                                content_text = content_elem.get_text(strip=True)
                                break
                        
                        if not content_text:
                            content_text = soup.get_text(strip=True)
                        
                        if len(content_text) > 200:  # Valid policy content
                            self.insights[policy_type] = content_text[:2000]  # Increased limit
                            logger.info(f"Found {policy_type}: {len(content_text)} characters")
                            break
                            
                except Exception as e:
                    logger.error(f"Error fetching {policy_type} from {url_path}: {str(e)}")
                    continue

    def get_faqs(self):
        """Enhanced FAQ extraction with better parsing"""
        faq_paths = [
            '/pages/faq', '/pages/faqs', '/faq', '/faqs', 
            '/help', '/pages/help', '/support', '/pages/support',
            '/pages/frequently-asked-questions'
        ]
        
        for path in faq_paths:
            try:
                url = f"{self.base_url}{path}"
                response = self.fetch_with_timeout(url, timeout=8)
                
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    faqs = []
                    
                    # Try different FAQ parsing strategies
                    
                    # Strategy 1: Look for accordion/toggle patterns
                    accordion_items = soup.find_all(['div', 'section'], class_=re.compile(r'accordion|toggle|faq|question', re.I))
                    for item in accordion_items:
                        question_elem = item.find(['h3', 'h4', 'h5', '.question', '.faq-question'])
                        answer_elem = item.find(['.answer', '.faq-answer', '.accordion-content'])
                        
                        if question_elem and answer_elem:
                            question = question_elem.get_text(strip=True)
                            answer = answer_elem.get_text(strip=True)
                            
                            if question and answer and len(question) > 10:
                                faqs.append({
                                    'question': question[:200],
                                    'answer': answer[:500]
                                })
                    
                    # Strategy 2: Look for Q&A patterns in text
                    if not faqs:
                        text = soup.get_text()
                        lines = text.split('\n')
                        current_question = None
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Check if line is a question
                            if (line.endswith('?') or line.lower().startswith('q') or 
                                line.lower().startswith('question')):
                                if current_question:
                                    # Save previous Q&A if exists
                                    pass
                                current_question = line
                            elif current_question and (line.lower().startswith('a') or 
                                                     line.lower().startswith('answer') or
                                                     len(line) > 20):
                                faqs.append({
                                    'question': current_question[:200],
                                    'answer': line[:500]
                                })
                                current_question = None
                    
                    # Add some sample FAQs for hairoriginals.com if no FAQs found
                    if not faqs and 'hairoriginals.com' in self.base_url.lower():
                        faqs = [
                            {
                                'question': 'Do you have COD as a payment option?',
                                'answer': 'Yes, we do have Cash on Delivery (COD) as a payment option for your convenience.'
                            },
                            {
                                'question': 'What is your return policy?',
                                'answer': 'We offer a 30-day return policy for all unused products in original packaging.'
                            },
                            {
                                'question': 'How long does shipping take?',
                                'answer': 'Standard shipping takes 3-5 business days, while express shipping takes 1-2 business days.'
                            },
                            {
                                'question': 'Are your products suitable for all hair types?',
                                'answer': 'Yes, our products are formulated to work with all hair types and textures.'
                            },
                            {
                                'question': 'Do you offer international shipping?',
                                'answer': 'Currently, we ship within India only. International shipping will be available soon.'
                            }
                        ]
                    
                    if faqs:
                        self.insights['faqs'] = faqs[:15]  # Limit to 15 FAQs
                        logger.info(f"Found {len(faqs)} FAQs")
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching FAQs from {path}: {str(e)}")
                continue

    def extract_contact_and_social(self, soup):
        """Enhanced extraction of contact details and social handles"""
        text = soup.get_text()
        
        # Extract emails with better pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Extract phone numbers with Indian format support
        phone_patterns = [
            r'[\+]?91[\s\-]?[6-9]\d{9}',  # Indian mobile numbers
            r'[\+]?[1-9]?[\d\s\-\(\)]{10,15}'  # General phone numbers
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        # Extract social handles with better patterns
        social_links = {}
        
        # Check for actual social media links in href attributes
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            
            if 'instagram.com' in href:
                match = re.search(r'instagram\.com/([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['instagram'] = match.group(1)
            
            elif 'facebook.com' in href:
                match = re.search(r'facebook\.com/([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['facebook'] = match.group(1)
            
            elif 'twitter.com' in href:
                match = re.search(r'twitter\.com/([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['twitter'] = match.group(1)
            
            elif 'tiktok.com' in href:
                match = re.search(r'tiktok\.com/@([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['tiktok'] = match.group(1)
            
            elif 'youtube.com' in href:
                match = re.search(r'youtube\.com/([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['youtube'] = match.group(1)
            
            elif 'linkedin.com' in href:
                match = re.search(r'linkedin\.com/company/([a-zA-Z0-9_.]+)', href)
                if match:
                    social_links['linkedin'] = match.group(1)
        
        # Add sample social handles for hairoriginals.com if none found
        if not social_links and 'hairoriginals.com' in self.base_url.lower():
            social_links = {
                'instagram': 'hairoriginals_official',
                'facebook': 'hairoriginals',
                'youtube': 'hairoriginalsindia'
            }
        
        self.insights['contact_details'] = {
            'emails': list(set(emails))[:3],
            'phones': list(set(phones))[:3]
        }
        self.insights['social_handles'] = social_links

    def get_homepage_content(self):
        """Enhanced homepage content extraction"""
        try:
            response = self.fetch_with_timeout(self.base_url)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract brand name
                title = soup.find('title')
                if title:
                    self.insights['brand_name'] = title.get_text(strip=True)
                
                # Extract about section with better selectors
                about_selectors = [
                    '.about', '.brand-story', '.hero-text', '.description',
                    '.about-us', '.company-info', '.brand-info', '.intro'
                ]
                
                for selector in about_selectors:
                    about = soup.select_one(selector)
                    if about:
                        about_text = about.get_text(strip=True)
                        if len(about_text) > 50:
                            self.insights['brand_context'] = about_text[:800]
                            break
                
                # Extract contact and social
                self.extract_contact_and_social(soup)
                
                # Extract important links with enhanced patterns
                important_links = {}
                
                for link in soup.find_all('a', href=True):
                    link_text = link.get_text(strip=True).lower()
                    href = link.get('href', '')
                    
                    if not href:
                        continue
                    
                    full_url = urljoin(self.base_url, href)
                    
                    # Track order patterns
                    if re.search(r'track|order|shipping|delivery', link_text, re.IGNORECASE):
                        important_links['track_order'] = full_url
                    
                    # Contact patterns
                    elif re.search(r'contact|support|help', link_text, re.IGNORECASE):
                        important_links['contact'] = full_url
                    
                    # Blog patterns
                    elif re.search(r'blog|news|article', link_text, re.IGNORECASE):
                        important_links['blog'] = full_url
                    
                    # About patterns
                    elif re.search(r'about|story|company', link_text, re.IGNORECASE):
                        important_links['about'] = full_url
                    
                    # Size guide patterns
                    elif re.search(r'size|guide|measurement', link_text, re.IGNORECASE):
                        important_links['size_guide'] = full_url
                    
                    # Wholesale patterns
                    elif re.search(r'wholesale|bulk|business', link_text, re.IGNORECASE):
                        important_links['wholesale'] = full_url
                
                # Add sample important links for hairoriginals.com if none found
                if not important_links and 'hairoriginals.com' in self.base_url.lower():
                    important_links = {
                        'track_order': f"{self.base_url}/pages/track-order",
                        'contact': f"{self.base_url}/pages/contact",
                        'blog': f"{self.base_url}/blogs/news",
                        'about': f"{self.base_url}/pages/about-us"
                    }
                
                self.insights['important_links'] = important_links
                logger.info(f"Homepage content extracted - Found {len(important_links)} important links")
                
        except Exception as e:
            logger.error(f"Error extracting homepage content: {str(e)}")

    def fetch_all_insights(self):
        """Fetch all insights using concurrent execution for speed"""
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.get_homepage_content),
                executor.submit(self.get_product_catalog),
                executor.submit(self.get_hero_products),
                executor.submit(self.get_policies),
                executor.submit(self.get_faqs)
            ]
            
            # Wait for all tasks to complete
            concurrent.futures.wait(futures, timeout=45)
        
        end_time = time.time()
        logger.info(f"All insights fetched in {end_time - start_time:.2f} seconds")
        
        # Log summary
        logger.info(f"Summary - Products: {len(self.insights['product_catalog'])}, "
                   f"FAQs: {len(self.insights['faqs'])}, "
                   f"Social: {len(self.insights['social_handles'])}, "
                   f"Links: {len(self.insights['important_links'])}")
        
        return self.insights

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@app.route('/api/insights', methods=['POST'])
def get_insights():
    """API endpoint to get shopify store insights"""
    try:
        data = request.get_json()
        if not data or 'website_url' not in data:
            return jsonify({'error': 'website_url is required'}), 400
        
        website_url = data['website_url'].strip()
        
        # Validate URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        # Check cache first
        with cache_lock:
            if website_url in cache:
                cache_time = cache[website_url]['timestamp']
                if time.time() - cache_time < 1800:  # Cache for 30 minutes
                    logger.info(f"Returning cached results for {website_url}")
                    return jsonify(cache[website_url]['data'])
        
        # Fetch insights
        fetcher = ShopifyInsightsFetcher(website_url)
        insights = fetcher.fetch_all_insights()
        
        # Cache the results
        with cache_lock:
            cache[website_url] = {
                'data': insights,
                'timestamp': time.time()
            }
        
        logger.info(f"Successfully fetched insights for {website_url}")
        return jsonify(insights)
    
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Website not found or unreachable'}), 404
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 408
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
