import streamlit as st
import json
from bs4 import BeautifulSoup
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download NLTK resources (stopwords and punkt tokenizer)
import nltk
nltk.download('stopwords')
nltk.download('punkt')

# Function to preprocess text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    # Remove punctuation and convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()
    # Tokenize the text and remove stopwords
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(filtered_tokens)

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


# Function to cluster articles
def cluster_articles(articles):
    # Extract title for clustering and preprocess
    content = [preprocess_text(article['title']) for article in articles]

    # Vectorize the content using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(content)

    # Apply K-Means clustering
    num_clusters = 6
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Assign clusters to articles
    for i, article in enumerate(articles):
        article['cluster'] = int(clusters[i])  # Convert cluster to int

    return articles


# Streamlit app
def main():
    st.title("News Scraping App")

    # Scrape news articles
    articles = scrape_news()

    # Perform clustering on the scraped articles
    clustered_articles = cluster_articles(articles)

    # Display the scraped and clustered articles
    for article in clustered_articles:
        st.write(f"Title: {article['title']}")
        st.write(f"Link: {article['link']}")
        st.write(f"Description: {article['description']}")
        st.write(f"Content: {article['content']}")
        st.write(f"Cluster: {article['cluster']}")
        st.write("---")

    # Save the scraped and clustered articles to a JSON file
    with open('bbc_articles_clustered.json', 'w', encoding='utf-8') as json_file:
        json.dump(clustered_articles, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
