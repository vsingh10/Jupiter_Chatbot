import requests
from bs4 import BeautifulSoup
import html2text
import json
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import time

print("Web Scraping Script Initialized")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

sitemap_url = "https://jupiter.money/sitemap.xml" 

def fetch_urls(sitemap_url):
    try:
        response_sitemap = requests.get(sitemap_url, headers=headers, timeout=10)
        if response_sitemap.status_code == 200:
            print("Sitemap fetched successfuly")
            root = ET.fromstring(response_sitemap.content)
            namespaces = namespace
            loc_tags = root.findall('.//ns:loc', namespaces)

            site_urls = [loc.text.strip() for loc in loc_tags]
            return site_urls
        else:
            print(f"Failed to fetch sitemap: {response_sitemap.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []
    
sitemap_urls = fetch_urls(sitemap_url)
print(f"Found {len(sitemap_urls)} URLs in the sitemap.")
print("Which are:", sitemap_urls)

# As these fetched URLS are XML URLs in thier own, now we look through them to check the number of urls

all_page_urls = []

for site_urls in sitemap_urls:
    print(f"\nFetching sitemap: {site_urls}")
    try:
        response = requests.get(site_urls, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"  ❌ Non-200 status code {response.status_code} for {site_urls}")
            continue

        root = ET.fromstring(response.text)

        urls = [loc.text.strip() for loc in root.findall(".//ns:loc", namespaces=namespace)]
        print(f"Found {len(urls)} URLs")
        print(f"URLs: {urls}")
        all_page_urls.extend(urls)

    except Exception as e:
        print(f"Exception while fetching {sitemap_url}: {e}")

print(f"\nTotal URLs collected: {len(all_page_urls)}")


html2text_instance = html2text.HTML2Text()
html2text_instance.images_to_alt = True
html2text_instance.body_width = 0
html2text_instance.single_line_break = True


all_data = []
error_urls = []

for url in all_page_urls:
    time.sleep(0.2)
    print(f"\nProcessing URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=50)
        if response.status_code !=200:
            print("Server Error")
            continue

        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()

        html = str(soup)
        text = html2text_instance.handle(html)

        try:
            title = soup.title.string.strip()
        except:
            path = urlparse(url).path
            title = path[1:].replace("/", "-") if path else "No Title"

        meta_description = soup.find("meta", attrs = {"name": "description"})
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})

        description = meta_description.get("content").strip() if meta_description else title

        keywords = meta_keywords.get("content").strip() if meta_keywords else "No Keywords"

        extracted_data = {
            "text": text,
            "metadata":{
                "title": title,
                "url": url,
                "description": description,
                "keywords": keywords,

            }
        }

        all_data.append(extracted_data)
        print(f"Processed {url} successfully")
    except Exception as e:
        print(f"Error processing {url}: {e}")
        error_urls.append(url)


#Saving
with open("dataset/scraped_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4, ensure_ascii=False)

print(f"\nTotal data entries collected: {len(all_data)}")
print("Data saved to scraped_data.json")
print(f"Total errors encountered: {len(error_urls)}")