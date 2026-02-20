#!/usr/bin/env python3
import urllib.request, urllib.parse, json

def get_wikipedia_image(search_term):
    search_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        'action': 'query', 'list': 'search', 'srsearch': search_term, 'srlimit': 1, 'format': 'json'
    })
    req = urllib.request.Request(search_url, headers={'User-Agent': 'FutquizBot/1.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    results = data.get('query', {}).get('search', [])
    if not results:
        return None, "No results"
    page_title = results[0]['title']
    img_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        'action': 'query', 'titles': page_title, 'prop': 'pageimages', 'pithumbsize': 240, 'format': 'json'
    })
    req2 = urllib.request.Request(img_url, headers={'User-Agent': 'FutquizBot/1.0'})
    with urllib.request.urlopen(req2, timeout=10) as r2:
        data2 = json.loads(r2.read())
    pages = data2.get('query', {}).get('pages', {})
    for page_id, page_data in pages.items():
        thumb = page_data.get('thumbnail', {})
        if thumb.get('source'):
            return thumb['source'], page_title
    return None, f"No image: {page_title}"

for name, term in [("Luis Díaz", "Luis Díaz footballer Colombia"), ("Giacinto Facchetti", "Giacinto Facchetti")]:
    url, info = get_wikipedia_image(term)
    print(f"{name}: {url}")
    print(f"  PAGE: {info}")
