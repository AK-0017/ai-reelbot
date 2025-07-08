import requests
import random
import time
import xml.etree.ElementTree as ET
import re
from html import unescape
from datetime import datetime
import os

# === API Keys ===
GNEWS_API_KEY = "f38754f89682fe24bf1569b49184b784"
NEWSDATA_API_KEY = "pub_fc870e4e4c2e400fbca87399f0d73123"

# === API Endpoints ===
GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"
NEWSDATA_ENDPOINT = "https://newsdata.io/api/1/news"
GOOGLE_RSS_URL = "https://news.google.com/rss/search?q=AI+OR+Artificial+Intelligence&hl=en-IN&gl=IN&ceid=IN:en"

# === Topics ===
TOPICS = [
    "AI chip ban", "OpenAI GPT-5", "Google Gemini", "AI regulation India",
    "AI startup funding", "NVIDIA earnings", "AI in healthcare", "AI in education",
    "AI in finance", "AI in cybersecurity", "AI in manufacturing", "AI in agriculture",
    "AI in transportation", "AI in entertainment", "AI in gaming", "AI in retail",
    "AI in smart cities", "AI in robotics", "AI in climate change", "AI in supply chain",
    "AI in social media", "AI in NLP", "AI in computer vision",
    "AI in autonomous vehicles", "AI in edge computing", "AI in virtual reality",
    "AI in augmented reality", "AI in quantum computing", "AI in IoT", "AI in blockchain"
]

# === Headers & CTAs ===
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CTAs = [
    "👉 Stay ahead in tech — follow us now!",
    "🔔 More stories like this, every day.",
    "🧠 Learn AI without the jargon — follow!",
    "📲 For daily AI updates, don't forget to follow."
]

HOOK_TEMPLATES = [
    "🚨 Breaking: {headline}",
    "🤖 Just In: {headline}",
    "💡 Quick Byte: {headline}",
    "🔥 Trending Now: {headline}",
    "👀 Must Know: {headline}",
    "📢 Here's what's happening: {headline}"
]

# === HTML Cleaner ===
def clean_html(raw_html: str) -> str:
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return unescape(clean_text.strip())

# === Google News RSS ===
def fetch_from_google_rss():
    print("🌐 Fetching from Google News RSS...")
    try:
        res = requests.get(GOOGLE_RSS_URL)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")
        results = []
        for item in items[:10]:
            title = clean_html(item.findtext("title", ""))
            description = clean_html(item.findtext("description", ""))
            url = item.findtext("link", "")
            if len(description.split()) < 20:
                continue
            results.append({
                "title": title,
                "description": description,
                "url": url
            })
        return results
    except Exception as e:
        print(f"⚠️ RSS error: {e}")
        return []

# === NewsData.io ===
def fetch_from_newsdata():
    print("🌐 Fetching from NewsData.io...")
    try:
        params = {
            "apikey": NEWSDATA_API_KEY,
            "q": "AI",
            "language": "en",
            "country": "in",
            "category": "technology"
        }
        res = requests.get(NEWSDATA_ENDPOINT, params=params)
        res.raise_for_status()
        data = res.json()
        results = []
        for a in data.get("results", []):
            title = clean_html(a.get("title", ""))
            description = clean_html(a.get("description", ""))
            url = a.get("link", "")
            if len(description.split()) < 20:
                continue
            results.append({
                "title": title,
                "description": description,
                "url": url
            })
        return results
    except Exception as e:
        print(f"⚠️ NewsData error: {e}")
        return []

# === GNews.io ===
def fetch_from_gnews():
    print("🌐 Fetching from GNews API...")
    all_results = []
    sampled_topics = random.sample(TOPICS, 10)
    today = datetime.now().strftime("%Y-%m-%d")
    for topic in sampled_topics:
        params = {
            "q": topic,
            "lang": "en",
            "country": "in",
            "max": 10,
            "token": GNEWS_API_KEY,
            "from": today,
            "to": today
        }
        try:
            response = requests.get(GNEWS_ENDPOINT, headers=HEADERS, params=params)
            if response.status_code == 200:
                data = response.json()
                for a in data.get("articles", []):
                    title = clean_html(a.get("title", ""))
                    description = clean_html(a.get("description", ""))
                    url = a.get("url", "")
                    if len(description.split()) < 20:
                        continue
                    all_results.append({
                        "title": title,
                        "description": description,
                        "url": url
                    })
        except Exception as e:
            print(f"⚠️ GNews error: {e}")
    return all_results

# === Combine All Sources ===
def fetch_news_from_all_sources():
    print("📰 Fetching latest AI/tech news from all sources...")
    rss = fetch_from_google_rss()
    newsdata = fetch_from_newsdata()
    gnews = fetch_from_gnews()
    combined = rss + rss + gnews + newsdata  # Weighted toward RSS
    if not combined:
        print("❌ No stories fetched from any source.")
    return combined

# === Script Generator ===
def generate_script(news):
    print("✅ Generating reel-style script...")
    scripts = []
    seen_titles = set()

    for article in news:
        headline = article.get("title", "").strip()
        summary = article.get("description", "").strip()
        url = article.get("url", "")

        if not headline or headline in seen_titles:
            continue
        seen_titles.add(headline)

        if not summary or summary.lower() == headline.lower():
            continue
        if len(summary.split()) < 20:
            continue

        hook = random.choice(HOOK_TEMPLATES).format(headline=headline)

        insight = "This shows how fast AI is changing our world."
        if "NVIDIA" in headline.upper():
            insight = "NVIDIA’s moves usually signal bigger trends in AI hardware."
        elif "OPENAI" in headline.upper():
            insight = "OpenAI’s every decision is shaping the future of intelligence."

        parts = [hook, summary, f"💡 Why it matters: {insight}", random.choice(CTAs)]
        script = "\n\n".join(parts)
        scripts.append(script)

    return scripts

# === Script Saver ===
def save_scripts(scripts, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "script.txt")
    with open(path, "w", encoding="utf-8") as f:
        for script in scripts:
            f.write(script.strip() + "\n\n")
    print(f"📄 Saved scripts to {path}")

# === Entrypoint (for testing) ===
if __name__ == "__main__":
    print("This script is meant to be used as a module in main.py")
