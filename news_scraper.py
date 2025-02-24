import asyncio
import nest_asyncio
from requests_html import AsyncHTMLSession
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import re
from newspaper import Article
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from pymongo.errors import DuplicateKeyError

# Fix event loop issue in Jupyter Notebook
nest_asyncio.apply()

# Function to extract news URLs from a given page
async def get_news_urls(base_url):
    session = AsyncHTMLSession()
    response = await session.get(base_url)
    await response.html.arender()  # Execute JavaScript

    urls = set()
    for link in response.html.find('a'):
        href = link.attrs.get("href", "")
        if href.startswith("/"):
            url = urljoin(base_url, href)
        else:
            url = href

        # Filter valid news links
        if url.startswith("http"):
            urls.add(url)

    return urls

# Function to generate XML Sitemap
def generate_sitemap(urls, output_file):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in urls:
        url_element = ET.Element("url")
        loc_element = ET.Element("loc")
        loc_element.text = url
        url_element.append(loc_element)
        urlset.append(url_element)

    tree = ET.ElementTree(urlset)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Sitemap saved as {output_file}")

# Main Execution (Handling Async)
async def main(city):
    city = city.lower().replace(" ", "-")
    all_urls = set()

    # Scraping Times of India (Pages 1 to 5)
    for page_num in range(1, 6):
        toi_url = f"https://timesofindia.indiatimes.com/city/{city}/{page_num}"
        urls = await get_news_urls(toi_url)
        all_urls.update(urls)

    # Scraping India TV News (Pages 6 to 10)
    for page_num in range(6, 11):
        indiatv_url = f"https://www.indiatvnews.com/topic/{city}/{page_num}"
        urls = await get_news_urls(indiatv_url)
        all_urls.update(urls)

    # Save all URLs in a sitemap
    generate_sitemap(all_urls, f"sitemap_{city}.xml")

# import xml.etree.ElementTree as ET
def clean_sitemap(city_input):
    """Keep only article URLs of the desired format from TOI and India TV."""
    try:
        # File names
        input_file = f"sitemap_{city_input}.xml"
        output_file = f"sitemap_{city_input}_cleaned.xml"

        # Load sitemap
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Namespace
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Regex patterns (New formats)
        toi_article_pattern = re.compile(rf"https://timesofindia\.indiatimes\.com/city/{city_input}/.+/articleshow/\d+\.cms$")
        indiatv_article_pattern = re.compile(rf"https://www\.indiatvnews\.com/{city_input}/.+-\d{{4}}-\d{{2}}-\d{{2}}-\d+$")

        # Filter URLs
        for url_element in root.findall("ns:url", namespace):
            loc_element = url_element.find("ns:loc", namespace)
            if loc_element is not None:
                url = loc_element.text
                # Keep only valid article URLs
                if not (toi_article_pattern.match(url) or indiatv_article_pattern.match(url)):
                    root.remove(url_element)

        # Save cleaned sitemap
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"✅ Cleaned sitemap saved to: {output_file}")

    except Exception as e:
        print(f"⚠️ Error processing sitemap: {e}")


def get_urls_from_sitemap(sitemap_file):
    """Parse XML sitemap and return a list of URLs."""
    try:
        tree = ET.parse(sitemap_file)
        root = tree.getroot()

        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [url_element.find("ns:loc", namespace).text for url_element in root.findall("ns:url", namespace)]

        return urls
    except Exception as e:
        print(f"⚠️ Error reading sitemap: {e}")
        return []


def scrape_article(url):
    """Scrape article using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            "url": url,
            "title": article.title,
            "text": article.text,
            "top_image": article.top_image,
            "publish_date": article.publish_date.isoformat() if article.publish_date else None,
            "scraped_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return None

def mainn(city_input):
    """Scrape and save articles from sitemap_{city_input}_cleaned.xml."""
    sitemap_file = f"sitemap_{city_input}_cleaned.xml"
    news_urls = get_urls_from_sitemap(sitemap_file)

    if not news_urls:
        print("⚠️ No URLs found in sitemap.")
        return

    print(f"🔗 Found {len(news_urls)} URLs in sitemap.")

    # Scrape articles and save them to MongoDB
    scraped_articles = []
    for i, url in enumerate(news_urls):
        print(f"📰 Scraping {i + 1}/{len(news_urls)}: {url}")
        article_data = scrape_article(url)

        if article_data:
            try:
                collection.insert_one(article_data)  # Save to MongoDB
                scraped_articles.append(article_data)
                print(f"✅ Saved: {article_data['title']}")
            except DuplicateKeyError:
                print(f"⚠️ Article already exists: {url}")
            except Exception as e:
                print(f"⚠️ Error saving to MongoDB: {e}")

        time.sleep(1)  # To avoid getting blocked

    print(f"\n✅ Saved {len(scraped_articles)} articles in MongoDB.")

# Step 1: Summarize text
def summarize_text(text, max_length=130, min_length=70):
    """Summarize text using BART model."""
    try:
        if len(text.split()) < 70:  # Skip summarization if too short
            return text
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"⚠️ Error summarizing text: {e}")
        return None


# Step 2: Translate text (English to Hindi)
def translate_text(text, src_lang="en_XX", tgt_lang="hi_IN"):
    """Translate text using mBART model."""
    try:
        tokenizer.src_lang = src_lang
        inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang))
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text
    except Exception as e:
        print(f"⚠️ Error translating text: {e}")
        return None


# Step 3: Classify article
def classify_article(text):
    """Classify article using zero-shot classification into one of five categories."""
    try:
        result = classifier(text, categories, multi_label=False)
        return result["labels"][0]  # Return the category with the highest score
    except Exception as e:
        print(f"⚠️ Error classifying text: {e}")
        return "Uncategorized"


# Step 4: Process and save articles
def process_and_save_articles():
    """Fetch, summarize, translate, classify, and save articles."""
    try:
        articles = collection.find({})
        total_articles = collection.count_documents({})
        processed_count = 0

        for article in articles:
            article_id = article["_id"]
            text = article.get("text", "")
            title = article.get("title", "")
            url = article.get("url", "")
            image = article.get("image", None)

            if text:
                summary = summarize_text(text)
                # translated_summary = translate_text(summary) if summary else None
                category = classify_article(text)

                if translated_summary:
                    document = {
                        "_id": article_id,
                        "title": title,
                        # "url": url,
                        "category": category,
                        "summary": summary,
                        # "translated_summary": translated_summary
                    }

                    if image:
                        document["image"] = image

                    try:
                        summary_collection.insert_one(document)
                        processed_count += 1
                        print(f"✅ Processed {processed_count}/{total_articles} articles. Category: {category}")
                    except DuplicateKeyError:
                        print(f"⚠️ Article already exists: {url}")

    except Exception as e:
        print(f"⚠️ Error processing articles: {e}")



if __name__ == "__main__":
    city_input = "varanasi"
    asyncio.run(main(city_input))
    print("✅ Scraping completed successfully!")
    clean_sitemap(city_input)
    
    # MongoDB Connection
    MONGO_URI = "mongodb+srv://anshikajyotijain:Saloni%401234@cluster0.u5jtr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client["news_database"]
    collection = db["articles"]
    collection.create_index("url", unique=True)

    mainn(city_input)

    summary_collection = db["summaries"]  # Target collection
# summary_collection.delete_many({})
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Load translation model (mBART)
    model_name = "facebook/mbart-large-50-many-to-many-mmt"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Load zero-shot classifier
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Categories
    categories = ["Politics", "Sports", "Business", "Entertainment", "Technology"]
    process_and_save_articles()
    print("✅ All articles processed, categorized, and saved successfully!")
