import csv
import time
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def scrape_articles(url):
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()
    driver.get(url)

    # Scroll down to load more content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse the HTML content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    article_links = soup.find_all('article')  # Assuming articles are contained within 'article' tags
    articles_data = []

    i = 1
    for link in article_links:
        print(f"scraping..  {i} / {len(article_links)}")
        i += 1

        article_url = link.find('a')['href']
        if not article_url.startswith("https://index.hu/mindekozben"):
            article_data = scrape_article_content(article_url)
            if article_data:
                articles_data.append(article_data)

    # Write the data to a CSV file
    write_to_csv(articles_data)
    print("Data written to csv")

    # Close the WebDriver
    driver.quit()
    print("Failed to fetch the webpage")

MAX_RETRIES = 3
RETRY_DELAY = 2

def scrape_article_content(article_url):
    article_data = {}
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(article_url)
            response.raise_for_status()  # Raise HTTPError for bad responses (e.g., 404, 500)
            break  # Break out of retry loop if successful
        except RequestException as e:
            print(f"Failed to fetch article '{article_url}'. Attempt {attempt + 1}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Maximum retries exceeded. Skipping article...")
                return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        parental_lock_element = soup.find('input', id='korhatar_elmult')
        if parental_lock_element:
            print(f"Article '{article_url}' requires age verification. Skipping...")
            return None

        title_element = soup.find('div', class_='content-title')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        date_element = soup.find('div', class_='datum')
        if date_element:
            for div in date_element.find_all('div', class_='fb-share'):
                div.extract()
            date = date_element.text.strip()
        else:
            date = "Date not found"

        content_element = soup.find('div', class_='cikk-torzs')

        if content_element:
            for excluded_class in ['linkpreview', 'postcontent', 'cikk-bottom-text-ad', 'social-stripe', 'microsite_microsite']:
                for div in content_element.find_all('div', class_=excluded_class):
                    div.extract()

            content = content_element.text.strip()
        else:
            content = "Content not found"

        lead_element = soup.find('div', class_='lead')
        if lead_element:
            content = lead_element.text.strip() + "\n" + content

        article_data['Country'] = "Hungary"
        article_data['Site'] = "Index.hu"
        article_data['URL'] = article_url
        article_data['Date'] = date
        article_data['Title'] = title
        article_data['Content'] = content

        return article_data
    else:
        print(f"Failed to fetch article: {article_url}")
        return None

def write_to_csv(data):
    with open('index.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for article in data:
            writer.writerow(article)

# Example usage:
url = "https://index.hu/24ora/?word=1&pepe=1&tol=1999-01-01&ig=2024-03-18&s=airbnb"  # Replace this with the URL of the webpage containing the list of articles
scrape_articles(url)