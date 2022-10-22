import re

import nltk

from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.downloader.download('vader_lexicon')


class TwitterSentimentAnalyzer:

    def __int__(self, text):
        self.text = text

    @staticmethod
    def clean_text(text):
        text = text.lower()
        text = re.sub(r"@[A-Za-z0-9]+", " ", text)
        text = re.sub(r"(@[A-Za-z0–9]+) | ([0-9A-Za-z \t]) | (\w+:\/\/\S+)", " ", text)
        text = re.sub(r"[^a-zA-Z.!?']", " ", text)
        text = re.sub(r" +", " ", text)
        return text

    def get_sentiment(self, text):
        text = self.clean_text(text)
        score = SentimentIntensityAnalyzer().polarity_scores(text)
        return score['compound']
