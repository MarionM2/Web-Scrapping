import streamlit as st
import json
from bs4 import BeautifulSoup
import requests

# Function to scrape news articles from the BBC website
def scrape_news():
    url = 'https://www.bbc.com/news/world'
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles_set = set()
        articles = []  # Initialize the list of articles

        for article in soup.find_all('div', class_='gs-c-promo'):
            title_element = article.find('h3', class_='gs-c-promo-heading__title').text.strip()

            # Check if the 'a' tag is found before accessing its attributes
            link_tag = article.find('a', class_='gs-c-promo-heading')
            if link_tag:
                link = url + link_tag.get('href', '').strip()
            else:
                link = ''

            # Check if the article with the same link already exists
            if link in articles_set:
                continue

            articles_set.add(link)

            # Check if the 'p' tag is found before accessing its text attribute
            description_tag = article.find('p', class_='gs-c-promo-summary')
            description = description_tag.text.strip() if description_tag else ''

            content = f"{title_element} {description}"  # Concatenate title and description for content
            articles.append({'title': title_element, 'link': link, 'description': description, 'content': content})

        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news articles: {e}")
        return []

# local deployment to Streamlit app
def main():
    st.title("News Scraping App")

    # Loading clustered articles from the JSON file
    with open('bbc_articles_clustered.json', 'r', encoding='utf-8') as json_file:
        clustered_articles = json.load(json_file)

    # Displaying the clustered articles
    for article in clustered_articles:
        st.write(f"Title: {article['title']}")
        st.write(f"Link: {article['link']}")
        st.write(f"Description: {article['description']}")
        st.write(f"Content: {article['content']}")
        st.write(f"Cluster: {article['cluster']}")
        st.write("---")

if __name__ == '__main__':
    main()



