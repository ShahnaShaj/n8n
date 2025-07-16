# -*- coding: utf-8 -*-
"""News_Scraper_Demo Enhanced with Location Extraction"""

import feedparser
from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import tldextract
import transformers
from fake_useragent import UserAgent
from transformers import pipeline

# ========== CONFIG ==========

RSS_FEEDS = [
    # Global Tech & Emerging Technologies
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://spectrum.ieee.org/feed",
    "https://www.technologyreview.com/feed/",

    # Regional Tech - Middle East & Global South
    "https://www.thenationalnews.com/rss/technology",
    "https://english.alarabiya.net/.mrss/en/technology.xml",
    "https://gulfnews.com/rssfeeds/technology",
    "https://www.arabnews.com/cat/technology/rss",
    "https://www.zawya.com/rss/technology",

    # Oil & Gas, Energy Transition, Sustainability
    "https://www.offshore-technology.com/feed/",
    "https://www.rigzone.com/news/rss/",
    "https://www.energyvoice.com/feed/",
    "https://cleantechnica.com/feed/",
    "https://feeds.feedburner.com/greentechmedia-all-content",
]

KEYWORDS = [
    "beta", "startup", "early access", "emerging", "tech", "technology",
    "ai", "artificial intelligence", "machine learning", "data science",
    "robotics", "innovation", "app", "launch", "software", "hardware",
    "cloud", "saas", "crypto", "blockchain", "web3", "5g", "iot", "vr", "ar",
    "digital transformation in oil and gas", "smart oil fields", "AI in oil and gas",
    "data analytics in oil and gas", "IoT in oil and gas", "automation in oil and gas",
    "robotics in oil and gas", "drones oil rig", "carbon capture", "green technology",
    "enhanced oil recovery", "seismic imaging", "offshore drilling", "rig inspection"
]

CUTOFF_DATE = datetime.now() - timedelta(days=30)
ua = UserAgent()
HEADERS = {'User-Agent': ua.random}

TRUSTED_DOMAINS = [
    "bbc.co.uk", "nytimes.com", "cnet.com", "wired.com", "theverge.com", "techcrunch.com",
    "offshore-technology.com", "rigzone.com", "reuters.com", "bloomberg.com"
]

# ========== LOCATION EXTRACTION ==========

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def extract_locations(text):
    try:
        entities = ner_pipeline(text)
        locations = set()
        for ent in entities:
            if ent['entity_group'] in ['LOC', 'GPE', 'ORG']:
                locations.add(ent['word'])
        return list(locations)
    except:
        return []

# ========== UTILITY FUNCTIONS ==========

def compute_trust_score(url, soup):
    parsed = urlparse(url)
    domain = tldextract.extract(parsed.netloc).registered_domain
    trust_score = 0
    if domain in TRUSTED_DOMAINS:
        trust_score += 0.5
    if parsed.scheme == "https":
        trust_score += 0.2
    if soup.find("time") or soup.find("meta", attrs={"name": "date"}):
        trust_score += 0.15
    if soup.find("meta", attrs={"name": "author"}):
        trust_score += 0.15
    return round(min(trust_score, 1.0), 2)

def extract_summary(soup):
    paragraphs = soup.find_all("p")
    text = ' '.join(p.get_text() for p in paragraphs)
    return text.strip()[:500]

def crawl_article(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if not res.ok:
            return None, 0
        soup = BeautifulSoup(res.text, "html.parser")
        summary = extract_summary(soup)
        trust = compute_trust_score(url, soup)
        return summary, trust
    except Exception as e:
        return None, 0

# ========== MAIN ==========

filtered_articles = []

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        if 'published_parsed' not in entry:
            continue

        published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        if published < CUTOFF_DATE:
            continue

        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")

        if any(kw.lower() in title.lower() for kw in KEYWORDS):
            summary_full, trust_score = crawl_article(link)
            if summary_full:
                locations = extract_locations(summary_full)
                filtered_articles.append({
                    "title": title.strip(),
                    "url": link,
                    "published": published.strftime("%Y-%m-%d"),
                    "summary": summary_full,
                    "trust_score": trust_score,
                    "locations": locations
                })

# ========== OUTPUT ==========

import sys
print(json.dumps(filtered_articles, ensure_ascii=False))
sys.stdout.flush()
