import csv
import requests
from bs4 import BeautifulSoup
import time

MAX_RETRIES = 3
RETRY_DELAY = 2


def scrape_articles():
    articles_data = []
    for page_num in range(1, 13):  # Assuming there are 13 pages
        url = f"https://hvg.hu/cimke/Airbnb/{page_num}"
        print(f"Scraping articles from page {page_num}...")
        page_articles = scrape_page_articles(url)
        if page_articles:
            articles_data.extend(page_articles)
        time.sleep(2)  # Add a delay between page requests
    write_to_csv(articles_data)
    print("All articles scraped and saved to csv")

def scrape_page_articles(url):
    article_links = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (e.g., 404, 500)
        soup = BeautifulSoup(response.content, 'html.parser')
        column_articlelist_div = soup.find('div', class_='column-articlelist')
        if column_articlelist_div:
            h2_elements = column_articlelist_div.find_all('h2', class_='heading-3')
            article_links = []
            for h2 in h2_elements:
                a_tag = h2.find('a')
                if a_tag:
                    article_links.append(a_tag)
        else:
            print("No div with class 'column-articlelist' found.")
    except requests.RequestException as e:
        print(f"Failed to fetch page: {url}")
        print(e)
    return [scrape_article_content("https://hvg.hu/" + link['href']) for link in article_links]

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

        title_element = soup.find('div', class_='article-title')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        date_element = soup.find('time', class_='article-datetime')
        if date_element:
            date = date_element.text.strip()
        else:
            date = "Date not found"

        content_element = soup.find('div', class_='article-main')
        if content_element:
            # Exclude elements with class 'banner-container'
            for banner in content_element.find_all(class_='placeholder-ad'):
                banner.decompose()
            for tags in content_element.find_all(class_='main-tag-container'):
                tags.decompose()
            for element in content_element.find_all(class_='embedly-card'):
                element.decompose()
            content = content_element.text.strip()
        else:
            content = "Content not found"

        article_data['Country'] = "Hungary"  # Adjust country if necessary
        article_data['Site'] = "hvg.hu"  # Adjust site name if necessary
        article_data['URL'] = article_url
        article_data['Date'] = date
        article_data['Title'] = title
        article_data['Content'] = content

        print(article_data)

        return article_data
    else:
        print(f"Failed to fetch article: {article_url}")
        return None

def write_to_csv(data):
    with open('hvg.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in data:
            writer.writerow(article)


# run the function
scrape_articles()