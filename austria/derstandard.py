import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MAX_RETRIES = 3
RETRY_DELAY = 2

def scrape_articles():
    articles_data = []
    
    driver = webdriver.Chrome()  # Initialize Chrome WebDriver
    driver.get("https://www.derstandard.at/search?query=airbnb&fd=1997-01-01&s=score")
    time.sleep(30)  # Wait for the page to load (adjust this delay as needed)

    for page_num in range(1, 12):  # Assuming there are 18 pages
        url = f"https://www.derstandard.at/search?n=&fd=1997-01-01&td=&s=date&query=airbnb&p={page_num}"
        page_articles = scrape_page_articles(driver, url, page_num)
        if page_articles:
            articles_data.extend(page_articles)
        time.sleep(2)  # Add a delay between page requests
    write_to_csv(articles_data)
    print("All articles scraped and saved to csv")
    
    driver.quit()

def scrape_page_articles(driver, url, page_num):
    article_links = []
    scraped_data = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 1)  # Adjust the timeout as needed
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article a")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.find_all('article')
        article_links = [a.find('a')['href'] for a in articles if a.find('a')]
    except Exception as e:
        print(f"Failed to fetch page: {url}")
        print(e)
        
    # Iterate over article links and call scrape_article_content
    for index, link in enumerate(article_links, start=1):
        print(f"Page {page_num}/11: Processing link {index}/{len(article_links)}")
        data = scrape_article_content(driver, "https://www.derstandard.at" + link)
        scraped_data.append(data)
    
    return scraped_data
def scrape_article_content(driver, article_url):
    print("Scraping " + article_url)
    article_data = {}
    try:
        driver.get(article_url)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        title_element = soup.find('h1', class_='article-title')
        if title_element:
            title = title_element.text.strip()
        else:
            title = "Title not found"

        # Wait for the date element to be present
        date_element = soup.find('p', class_='article-pubdate')
        if date_element:
            date = date_element.text.strip()
        else:
            date = "Date not found"

        content_element = soup.find('div', class_='article-body')
        if content_element:
            # Exclude elements with class 'banner-container'
            for element in content_element.find_all('div', {'data-section-type': 'image'}):
                element.decompose()
            for element in content_element.find_all('ad-container'):
                element.decompose()
            for element in content_element.find_all('dst-community-reactions'):
                element.decompose()
            for element in content_element.find_all('aside'):
                element.decompose()
            content = content_element.text.strip()
        else:
            content = "Content not found"

        article_data['Country'] = "Austria"  # Adjust country if necessary
        article_data['Site'] = "derstandard.at"  # Adjust site name if necessary
        article_data['URL'] = article_url
        article_data['Date'] = date
        article_data['Title'] = title
        article_data['Content'] = content

        print(article_data)

        return article_data
    except Exception as e:
        print(f"Error while scraping article: {article_url}")
        print(e)
        return None

def write_to_csv(data):
    with open('derstandard.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Country', 'Date', 'Site', 'URL', 'Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in data:
            writer.writerow(article)


# run the function
scrape_articles()