import os
import requests
from bs4 import BeautifulSoup
import html2text
import feedparser
from datetime import datetime
import pytz

# Configuration
RSS_FEED_URL = "https://awsmorocco.com/rss"
IMAGES_DIR = "assets/images/medium"
POSTS_DIR = "content/english/blog"

def download_image(image_url):
    """Downloads an image and returns the local file path."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    local_filename = os.path.join(IMAGES_DIR, os.path.basename(image_url))
    if not os.path.exists(local_filename):  # Check if image already exists
        with requests.get(image_url, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    return local_filename

def convert_html_to_md(html_content):
    """Converts HTML content to Markdown."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    return h.handle(html_content)

def process_entry(entry):
    """Processes a single RSS entry."""
    soup = BeautifulSoup(entry.content[0].value, 'html.parser')
    # Download and replace images
    for img in soup.find_all('img'):
        image_url = img['src']
        local_image_path = download_image(image_url)
        img['src'] = os.path.join("/", local_image_path)
    
    markdown_content = convert_html_to_md(str(soup))
    return markdown_content

def main():
    feed = feedparser.parse(RSS_FEED_URL)
    if not os.path.exists(POSTS_DIR):  # Ensure the posts directory exists
        os.makedirs(POSTS_DIR)
    for entry in feed.entries:
        safe_title = entry.title.replace(' ', '_').replace('/', '_').lower()
        filename = os.path.join(POSTS_DIR, safe_title + '.md')
        
        # Skip if file already exists
        if os.path.isfile(filename):
            print(f"File already exists for: {entry.title}, skipping.")
            continue
        
        markdown_content = process_entry(entry)
        metadata = f"""
---
title: "{entry.title}"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: {datetime.now(pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')}
author: "{entry.get('dc:creator', 'Unknown Author')}"
---

"""
        full_content = metadata + markdown_content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"Generated markdown for: {entry.title}")

if __name__ == "__main__":
    main()
