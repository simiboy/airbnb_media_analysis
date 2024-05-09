import csv
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

MAX_RETRIES = 3
RETRY_DELAY = 2

def scrape_articles():
    articles_data = []
    with open('krone_links.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        article_links = ['https://www.krone.at/' + row[0] for row in reader]
    i = 0
    for link in article_links:
        i += 1
        print(f"Scraping {i}/{len(article_links)}")
        article_data = scrape_article_content(link)
        if article_data:
            articles_data.append(article_data)
        time.sleep(2)  # Add a delay between requests
    write_to_csv(articles_data)
    print("All articles scraped and saved to csv")

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

        title_element = soup.find('h1', class_='krn_editable')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        date_element = soup.find('div', class_='bc__date')
        if date_element:
            date = date_element.text.strip()
        else:
            date = "Date not found"

        content_parts = []
        content_divs = soup.find_all('div', class_='c_outer') + soup.find_all('div', class_='c_content')
        for div in content_divs:
            content = div.text.strip()
            # Exclude certain divs
            for exclude_class in ['c_newsletter-signup-article', 'c_linkbox', 'c_image']:
                for element in div.find_all('div', class_=exclude_class):
                    element.decompose()
            content_parts.append(content)
        content = ' '.join(content_parts)

        article_data['Country'] = "Austria"  # Adjust country if necessary
        article_data['Site'] = "krone.at"  # Adjust site name if necessary
        article_data['URL'] = article_url
        article_data['Date'] = date
        article_data['Title'] = title
        article_data['Content'] = content

        return article_data
    else:
        print(f"Failed to fetch article: {article_url}")
        return None

def write_to_csv(data):
    with open('krone.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in data:
            writer.writerow(article)

# run the function
scrape_articles()