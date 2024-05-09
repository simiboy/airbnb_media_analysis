import csv
import requests
from bs4 import BeautifulSoup
import time

MAX_RETRIES = 3
RETRY_DELAY = 2

def scrape_articles():
    articles_data = []
    for page_num in range(0, 331, 10):  #331
        url = f"https://search.seznam.cz/s/novinky/?q=airbnb&count=10&pId=iL8pk_Ahkc3_1Y5xkCXk&sort=time&ribbon=novinky&from={page_num}"
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
        article_links = soup.find_all('a', class_='cfd7401e28f')
    except requests.RequestException as e:
        print(f"Failed to fetch page: {url}")
        print(e)
    
    scraped_data = []
    for index, link in enumerate(article_links, start=1):
        print(f"Page {(int(page_num/10) + 1)}/34: Processing link {index}/{len(article_links)} -> {link['href']}")
        data = scrape_article_content(link['href'])
        scraped_data.append(data)
    
    return scraped_data

def scrape_article_content(article_url):
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

        title_element = soup.find('h1')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        date_element = soup.find('time', class_='mol-formatted-date')
        if date_element:
            date = date_element.text.strip()
        else:
            date = "Date not found"

        content_elements = soup.find_all(['p', 'h2'], class_='c_aW' or 'c_aC')
        for element in content_elements:
            for span_element in element.find_all('a', class_="c_ak"):
                span_element.decompose()

        content = ' '.join(element.text.strip() for element in content_elements)

        article_data['Country'] = "Czechia"  # Adjust country if necessary
        article_data['Site'] = "seznam.cz"  # Adjust site name if necessary
        article_data['URL'] = article_url
        article_data['Title'] = title.replace('\xa0', '')
        article_data['Date'] = date.replace('\xa0', '')
        article_data['Content'] = content.replace('\xa0', '').replace('Reklama', '')

        return article_data
    else:
        print(f"Failed to fetch article: {article_url}")
        return None

def write_to_csv(data):
    with open('seznam.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in data:
            if article is not None: 
                writer.writerow(article)

# Run function
scrape_articles()
