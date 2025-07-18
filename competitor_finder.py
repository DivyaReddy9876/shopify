from googlesearch import search

def find_competitors(brand_url: str, max_results: int = 3) -> list[str]:
    brand_name = brand_url.split("//")[-1].split(".")[0]  # crude name extraction
    query = f"{brand_name} competitors site:shopify.com"
    
    results = []
    for result in search(query, num_results=10):
        if brand_name not in result and "/products" in result:
            results.append(result.split("/products")[0])
            if len(results) >= max_results:
                break
    return list(set(results))  # remove duplicates
