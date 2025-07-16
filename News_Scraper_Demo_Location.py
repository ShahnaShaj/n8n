import feedparser
from datetime import datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import tldextract
from fake_useragent import UserAgent

# ========== CONFIG ==========

RSS_FEEDS = [
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://hnrss.org/frontpage",
    "https://www.cnet.com/rss/news/",
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://www.offshore-technology.com/feed/",
    "https://www.rigzone.com/news/rss/"
    "https://www.thenationalnews.com/rss/technology",            # UAE & regional innovation
    "https://english.alarabiya.net/.mrss/en/technology.xml",     # GCC + international tech
    "https://gulfnews.com/rssfeeds/technology",                  # UAE & MENA tech/business
    "https://www.arabnews.com/cat/technology/rss",               # KSA-focused tech & development
    "https://www.zawya.com/rss/technology",
    "https://www.offshore-technology.com/feed/",                 # ADNOC-relevant offshore tech
    "https://www.rigzone.com/news/rss/",                         # Oil & gas operations, tech
    "https://www.energyvoice.com/feed/",                         # Energy, transition, innovation
    "https://cleantechnica.com/feed/",                           # Renewables + clean energy tech
    "https://feeds.feedburner.com/greentechmedia-all-content", 
]
KEYWORDS = [
    # General Tech & Startup
    "beta", "startup", "early access", "emerging", "tech", "technology",
    "ai", "artificial intelligence", "machine learning", "data science",
    "robotics", "innovation", "app", "launch", "software", "hardware",
    "cloud", "saas", "crypto", "blockchain", "web3", "5g", "iot", "vr", "ar","sensors",

    # Oil & Gas + Tech Integration
    "digital transformation in oil and gas", "smart oil fields", "AI in oil and gas",
    "data analytics in oil and gas", "IoT in oil and gas", "automation in oil and gas",
    "robotics in oil and gas", "drones oil rig", "carbon capture", "green technology",
    "enhanced oil recovery", "seismic imaging", "offshore drilling", "rig inspection","oil", "gas", "drill", "rig", "platform", "refinery", "pipeline", "opec", "adnoc",
    "explosion", "merger", "acquisition", "carbon", "hydrocarbon", "tank", "leak", "barrel",
    "petroleum", "diesel", "lng", "offshore", "shutdown", "shipping", "contract", "investment","eco",
    "netzero", "sustainablity", "energy"
]

CUTOFF_DATE = datetime.now() - timedelta(days=30)
ua = UserAgent()
HEADERS = {'User-Agent': ua.random}

TRUSTED_DOMAINS = [
    "bbc.co.uk", "nytimes.com", "cnet.com", "wired.com", "theverge.com", "techcrunch.com",
    "offshore-technology.com", "rigzone.com", "reuters.com", "bloomberg.com"
]

# ========== IMPACT KEYWORDS ==========

IMPACT_KEYWORDS = {
    "critical": [
        # Severe/urgent issues
        "explosion", "shutdown", "leak", "spill", "fire", "strike",
        "sanction", "blockade", "attack", "accident", "gas leak",
        "blast", "evacuation", "collapse", "fatality", "shutdown",
        "pipeline rupture", "spillover", "contamination", "shutdown",
        "equipment failure", "blackout", "shutdown"
    ],
    "high": [
        # Core oil & gas industry terms & major business events
        "oil", "gas", "drilling", "refining", "shipping", "stock",
        "opec", "adnoc", "offshore", "rig", "contract", "merger",
        "acquisition", "investment", "regulation", "carbon",
        "refinery", "export", "terminal", "partnership", "discovery",
        "production", "lease", "pipeline", "shipment", "oilfield",
        "well", "fossil", "barrel", "petroleum", "upstream",
        "downstream", "midstream", "platform", "operator", "drill",
        "hydrocarbon", "seismic", "wellhead", "tank", "storage",
        "export", "import", "storage", "gasoline", "diesel", "fuel",
        "gas plant", "refinery", "petrochemical", "storage tank",
        "flare", "compressor", "valve", "energy", "eco", "sustainability"
    ],
    "medium": [
        "digital transformation", "robotics", "automation", "ai in oil and gas",
        "data analytics", "emissions reduction", "sustainability", "energy transition",
        "renewable integration", "smart oil fields", "digital twin", "asset monitoring",
        "hydrogen project", "carbon neutrality", "net zero", "environmental compliance",
        "natural language processing", "machine learning model", "predictive maintenance",
        "edge computing", "iot in oil and gas", "drones for inspection", "real-time analytics",
        "ai infrastructure", "computer vision", "enterprise ai", "semantic search",
        "generative ai", "open source llm", "foundation model", "ai agent", "chatbot in oil and gas"
    ],
    "low": [
        "startup", "app", "beta", "cloud", "web3", "saas", "vr", "ar",
        "tech trends", "new gadget", "early access", "mobile platform", "productivity tool",
        "code tool", "developer platform", "browser extension", "smartphone", "tablet",
        "wearable tech", "user interface", "ui update", "ux improvement", "bug fix"
    ]
}


# ========== COUNTRY DB ==========

COUNTRY_DB = {
    "afghanistan": (33.9391, 67.7100),
    "albania": (41.1533, 20.1683),
    "algeria": (28.0339, 1.6596),
    "andorra": (42.5078, 1.5211),
    "angola": (-11.2027, 17.8739),
    "antigua and barbuda": (17.0608, -61.7964),
    "argentina": (-38.4161, -63.6167),
    "armenia": (40.0691, 45.0382),
    "australia": (-25.2744, 133.7751),
    "austria": (47.5162, 14.5501),
    "azerbaijan": (40.1431, 47.5769),
    "bahamas": (25.0343, -77.3963),
    "bahrain": (26.0667, 50.5577),
    "bangladesh": (23.6850, 90.3563),
    "barbados": (13.1939, -59.5432),
    "belarus": (53.7098, 27.9534),
    "belgium": (50.5039, 4.4699),
    "belize": (17.1899, -88.4976),
    "benin": (9.3077, 2.3158),
    "bhutan": (27.5142, 90.4336),
    "bolivia": (-16.2902, -63.5887),
    "bosnia and herzegovina": (43.9159, 17.6791),
    "botswana": (-22.3285, 24.6849),
    "brazil": (-14.2350, -51.9253),
    "brunei": (4.5353, 114.7277),
    "bulgaria": (42.7339, 25.4858),
    "burkina faso": (12.2383, -1.5616),
    "burundi": (-3.3731, 29.9189),
    "cambodia": (12.5657, 104.9910),
    "cameroon": (7.3697, 12.3547),
    "canada": (56.1304, -106.3468),
    "cape verde": (16.5388, -23.0418),
    "central african republic": (6.6111, 20.9394),
    "chad": (15.4542, 18.7322),
    "chile": (-35.6751, -71.5430),
    "china": (35.8617, 104.1954),
    "colombia": (4.5709, -74.2973),
    "comoros": (-11.6455, 43.3333),
    "congo (brazzaville)": (-0.2280, 15.8277),
    "congo (kinshasa)": (-4.0383, 21.7587),
    "costa rica": (9.7489, -83.7534),
    "croatia": (45.1000, 15.2000),
    "cuba": (21.5218, -77.7812),
    "cyprus": (35.1264, 33.4299),
    "czech republic": (49.8175, 15.4730),
    "denmark": (56.2639, 9.5018),
    "djibouti": (11.8251, 42.5903),
    "dominica": (15.4149, -61.3700),
    "dominican republic": (18.7357, -70.1627),
    "ecuador": (-1.8312, -78.1834),
    "egypt": (26.8206, 30.8025),
    "el salvador": (13.7942, -88.8965),
    "equatorial guinea": (1.6508, 10.2679),
    "eritrea": (15.1794, 39.7823),
    "estonia": (58.5953, 25.0136),
    "eswatini": (-26.5225, 31.4659),
    "ethiopia": (9.1450, 40.4897),
    "fiji": (-17.7134, 178.0650),
    "finland": (61.9241, 25.7482),
    "france": (46.6034, 1.8883),
    "gabon": (-0.8037, 11.6094),
    "gambia": (13.4432, -15.3101),
    "georgia": (42.3154, 43.3569),
    "germany": (51.1657, 10.4515),
    "ghana": (7.9465, -1.0232),
    "greece": (39.0742, 21.8243),
    "grenada": (12.1165, -61.6790),
    "guatemala": (15.7835, -90.2308),
    "guinea": (9.9456, -9.6966),
    "guinea-bissau": (11.8037, -15.1804),
    "guyana": (4.8604, -58.9302),
    "haiti": (18.9712, -72.2852),
    "honduras": (13.2000, -87.2200),
    "hungary": (47.1625, 19.5033),
    "iceland": (64.9631, -19.0208),
    "india": (20.5937, 78.9629),
    "indonesia": (-0.7893, 113.9213),
    "iran": (32.4279, 53.6880),
    "iraq": (33.2232, 43.6793),
    "ireland": (53.1424, -7.6921),
    "israel": (31.0461, 34.8516),
    "italy": (41.8719, 12.5674),
    "ivory coast": (7.5400, -5.5471),
    "jamaica": (18.1096, -77.2975),
    "japan": (36.2048, 138.2529),
    "jordan": (30.5852, 36.2384),
    "kazakhstan": (48.0196, 66.9237),
    "kenya": (-0.0236, 37.9062),
    "kiribati": (1.8709, -157.3630),
    "kosovo": (42.6026, 20.9020),
    "kuwait": (29.3759, 47.9774),
    "kyrgyzstan": (41.2044, 74.7661),
    "laos": (19.8563, 102.4955),
    "latvia": (56.8796, 24.6032),
    "lebanon": (33.8547, 35.8623),
    "lesotho": (-29.6099, 28.2336),
    "liberia": (6.4281, -9.4295),
    "libya": (26.3351, 17.2283),
    "liechtenstein": (47.1660, 9.5554),
    "lithuania": (55.1694, 23.8813),
    "luxembourg": (49.8153, 6.1296),
    "madagascar": (-18.7669, 46.8691),
    "malawi": (-13.2543, 34.3015),
    "malaysia": (4.2105, 101.9758),
    "maldives": (3.2028, 73.2207),
    "mali": (17.5707, -3.9962),
    "malta": (35.9375, 14.3754),
    "marshall islands": (7.1315, 171.1845),
    "mauritania": (21.0079, -10.9408),
    "mauritius": (-20.3484, 57.5522),
    "mexico": (23.6345, -102.5528),
    "micronesia": (7.4256, 150.5508),
    "moldova": (47.4116, 28.3699),
    "monaco": (43.7384, 7.4246),
    "mongolia": (46.8625, 103.8467),
    "montenegro": (42.7087, 19.3744),
    "morocco": (31.7917, -7.0926),
    "mozambique": (-18.6657, 35.5296),
    "myanmar": (21.9162, 95.9560),
    "namibia": (-22.9576, 18.4904),
    "nauru": (-0.5228, 166.9315),
    "nepal": (28.3949, 84.1240),
    "netherlands": (52.1326, 5.2913),
    "new zealand": (-40.9006, 174.8860),
    "nicaragua": (12.8654, -85.2072),
    "niger": (17.6078, 8.0817),
    "nigeria": (9.0820, 8.6753),
    "north korea": (40.3399, 127.5101),
    "north macedonia": (41.9981, 21.4254),
    "norway": (60.4720, 8.4689),
    "oman": (21.5126, 55.9233),
    "pakistan": (30.3753, 69.3451),
    "palau": (7.5149, 134.5825),
    "panama": (8.5380, -80.7821),
    "papua new guinea": (-6.3149, 143.9555),
    "paraguay": (-23.4425, -58.4438),
    "peru": (-9.1900, -75.0152),
    "philippines": (13.4100, 122.5600),
    "poland": (51.9194, 19.1451),
    "portugal": (39.3999, -8.2245),
    "qatar": (25.276987, 51.520008),
    "romania": (45.9432, 24.9668),
    "russia": (61.5240, 105.3188),
    "rwanda": (-1.9403, 29.8739),
    "saint kitts and nevis": (17.3578, -62.7830),
    "saint lucia": (13.9094, -60.9789),
    "saint vincent and the grenadines": (13.2528, -61.1971),
    "samoa": (-13.7590, -172.1046),
    "san marino": (43.9333, 12.4500),
    "sao tome and principe": (0.1864, 6.6131),
    "saudi arabia": (23.8859, 45.0792),
    "senegal": (14.4974, -14.4524),
    "serbia": (44.0165, 21.0059),
    "seychelles": (-4.6796, 55.4919),
    "sierra leone": (8.4606, -11.7799),
    "singapore": (1.3521, 103.8198),
    "slovakia": (48.6690, 19.6990),
    "slovenia": (46.1512, 14.9955),
    "solomon islands": (-9.6457, 160.1562),
    "somalia": (5.1521, 46.1996),
    "south africa": (-30.5595, 22.9375),
    "south korea": (35.9078, 127.7669),
    "south sudan": (6.8769, 31.3069),
    "spain": (40.4637, -3.7492),
    "sri lanka": (7.8731, 80.7718),
    "sudan": (12.8628, 30.2176),
    "suriname": (3.9193, -56.0278),
    "sweden": (60.1282, 18.6435),
    "switzerland": (46.8182, 8.2275),
    "syria": (34.8021, 38.9968),
    "taiwan": (23.6978, 120.9605),
    "tajikistan": (38.8610, 71.2761),
    "tanzania": (-6.3690, 34.8888),
    "thailand": (15.8700, 100.9925),
    "timor-leste": (-8.8742, 125.7275),
    "togo": (8.6195, 0.8248),
    "tonga": (-21.1789, -175.1982),
    "trinidad and tobago": (10.6918, -61.2225),
    "tunisia": (33.8869, 9.5375),
    "turkey": (38.9637, 35.2433),
    "turkmenistan": (38.9697, 59.5563),
    "tuvalu": (-7.1095, 177.6493),
    "uganda": (1.3733, 32.2903),
    "ukraine": (48.3794, 31.1656),
    "united arab emirates": (24.4667, 54.3667),
    "united kingdom": (55.3781, -3.4360),
    "united states": (37.0902, -95.7129),
    "uruguay": (-32.5228, -55.7658),
    "uzbekistan": (41.3775, 64.5853),
    "vanuatu": (-15.3767, 166.9592),
    "venezuela": (6.4238, -66.5897),
    "vietnam": (14.0583, 108.2772),
    "yemen": (15.5527, 48.5164),
    "zambia": (-13.1339, 27.8493),
    "zimbabwe": (-19.0154, 29.1549)
}

DOMAIN_COUNTRY_MAP = {
    "bbc.co.uk": "united kingdom",
    "nytimes.com": "usa",
    "cnet.com": "usa",
    "wired.com": "usa",
    "theverge.com": "usa",
    "techcrunch.com": "usa",
    "offshore-technology.com": "global",
    "rigzone.com": "global",
    "reuters.com": "usa",
    "bloomberg.com": "usa"
}

# ========== FUNCTIONS ==========

def evaluate_impact(title, summary=""):
    text = f"{title} {summary}".lower()
    for level in ["critical", "high", "medium", "low"]:
        for keyword in IMPACT_KEYWORDS[level]:
            if keyword in text:
                return level
    return "low"

def extract_country_name(text, source_url):
    text_lower = text.lower()
    for country in COUNTRY_DB:
        if country in text_lower:
            return country.title()

    parsed = urlparse(source_url)
    domain = parsed.netloc.replace("www.", "")
    fallback_country = DOMAIN_COUNTRY_MAP.get(domain)
    if fallback_country:
        return fallback_country.title()

    return None

def get_country_coordinates(country_name):
    if not country_name:
        return None, None
    coords = COUNTRY_DB.get(country_name.lower())
    if coords:
        return coords
    return None, None

def compute_trust_score(url, soup):
    parsed = urlparse(url)
    domain = tldextract.extract(parsed.netloc).top_domain_under_public_suffix
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
    except Exception:
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
                impact = evaluate_impact(title, summary_full)
                country = extract_country_name(f"{title} {summary_full}", link)
                latitude, longitude = get_country_coordinates(country)

                filtered_articles.append({
                    "title": title.strip(),
                    "url": link,
                    "published": published.strftime("%Y-%m-%d"),
                    "summary": summary_full,
                    "trust_score": trust_score,
                    "impact": impact,
                    "location_country": country,
                    "latitude": latitude,
                    "longitude": longitude
                })

# ========== OUTPUT ==========

article_array = [
    {
        "title": article["title"],
        "url": article["url"],
        "published": article["published"],
        "summary": article["summary"],
        "trust_score": article["trust_score"],
        "impact": article["impact"],
        "location_country": article["location_country"],
        "latitude": article["latitude"],
        "longitude": article["longitude"]
    }
    for article in filtered_articles
]

print(json.dumps(article_array, indent=4, ensure_ascii=False))


