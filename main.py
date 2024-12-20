from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
import streamlit as st
import pickle
import re
from ntscraper import Nitter

# Downloading stopwords - using Streamlit's caching
@st.cache_resource
def load_stopwords():
    nltk.download('stopwords')
    return stopwords.words('english')

# Loading model and vectorizer 
@st.cache_resource
def load_model_and_vectorizer():
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    return model, vectorizer

# Defining sentiment prediction function
def predict_sentiment(text, model, vectorizer, stop_words):
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stop_words]
    text = ' '.join(text)
    text = [text]
    text = vectorizer.transform(text)
    
    # Predict sentiment
    sentiment = model.predict(text)
    return "Negative" if sentiment == 0 else "Positive"

# Initializing Nitter scraper
@st.cache_resource
def initialize_scraper():
    return Nitter(log_level=1)

# Function to create a colored card
def create_card(tweet_text, sentiment):
    color = "#90EE90" if sentiment == "Positive" else "#FF6961" # green is positive else red
    card = f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <h5 style="color: white;">{sentiment} Sentiment</h5>
        <p style="color: white;">{tweet_text}</p>
    </div>
    """
    return card

def main():
    st.title("Twitter Sentiment Analysis")

    # Loading stopwords, model, vectorizer, and scraper
    stop_words = load_stopwords()
    model, vectorizer = load_model_and_vectorizer()
    scraper = initialize_scraper()
    # User input: either text input or Twitter username
    option = st.selectbox("Choose an option", ["Input text", "Get tweets from user"])
    
    if option == "Input text":
        text_input = st.text_area("Enter text to analyze sentiment")
        if st.button("Analyze"):
            sentiment = predict_sentiment(text_input, model, vectorizer, stop_words)
            st.write(f"Sentiment: {sentiment}")

    elif option == "Get tweets from user":
        username = st.text_input("Enter Twitter username")
        if st.button("Fetch Tweets"):
            tweets_data = scraper.get_tweets(username, mode='user', number=5)
            if 'tweets' in tweets_data: 
                for tweet in tweets_data['tweets']:
                    tweet_text = tweet['text'] 
                    sentiment = predict_sentiment(tweet_text, model, vectorizer, stop_words)  # Predicting sentiment of the tweet text
                    # Creating and displaying the colored card for the tweet
                    card = create_card(tweet_text, sentiment)
                    st.markdown(card , unsafe_allow_html=True)
            else:
                st.write("No tweets found or an error occurred.")

if __name__ == "__main__":
    main()
