import csv
import requests
from bs4 import BeautifulSoup
import time

MAX_RETRIES = 3
RETRY_DELAY = 2

def scrape_articles():
    articles_data = []
    for page_num in range(1, 33):
        url = f"https://hledej.idnes.cz/clanky.aspx?q=airbnb&strana={page_num}"
        print(f"Scraping articles from page {page_num}...")
        page_articles = scrape_page_articles(page_num, url)
        if page_articles:
            articles_data.extend(page_articles)
        time.sleep(2)  # Add a delay between page requests
    write_to_csv(articles_data)
    print("All articles scraped and saved to csv")

def scrape_page_articles(page_num, url):
    article_links = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (e.g., 404, 500)
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = soup.find_all('a', class_='title')
    except requests.RequestException as e:
        print(f"Failed to fetch page: {url}")
        print(e)
    
    scraped_data = []
    for index, link in enumerate(article_links, start=1):
        print(f"Page {page_num}/33: Processing link {index}/{len(article_links)} ---> {link['href']}")
        data = scrape_article_content(link['href'])
        scraped_data.append(data)
    
    return scraped_data

def scrape_article_content(article_url):
    if  article_url.startswith("https://www.idnes.cz/wiki") | article_url.startswith("https://www.idnes.cz/jenprozeny/cosmopolitan/"):
        print("Skipping")
        return None
    article_data = {}
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(article_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (e.g., 404, 500)
            break  # Break out of retry loop if successful
        except requests.RequestException as e:
            print(f"Failed to fetch article '{article_url}'. Attempt {attempt + 1}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Maximum retries exceeded. Skipping article...")
                return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        content_element = soup.find('div', class_='content')

        title_element = content_element.find('h1')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        date_element = content_element.find('span', class_='time-date')
        if date_element:
            date = date_element.text.strip()
        else:
            date = "Date not found"

            
        content_element = content_element.find('div', class_='text')

        if content_element:
            # Exclude elements with class 'banner-container'
            for element in content_element.find_all('div', {'data-redistribute': 'ad'}):
                element.decompose()
            for element in content_element.find_all(class_='artmeta'):
                element.decompose()
            for element in content_element.find_all(class_='artmeta'):
                element.decompose()
            content = content_element.text.strip()
        else:
            content = "Content not found"

        
        lead_element = content_element.find('div', class_='opener')
        if lead_element:
            content = lead_element.text.strip() + "\n" + content

        article_data['Country'] = "Czechia"  # Adjust country if necessary
        article_data['Site'] = "idnes.cz"  # Adjust site name if necessary
        article_data['URL'] = article_url
        article_data['Date'] = date
        article_data['Title'] = title
        article_data['Content'] = content

        return article_data
    else:
        print(f"Failed to fetch article: {article_url}")
        return None

def write_to_csv(data):
    with open('idnes.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in data:
            if article is not None: 
                writer.writerow(article)

# Run function
scrape_articles()