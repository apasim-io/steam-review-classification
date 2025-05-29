# all libraries from a3
import argparse
import time

from collections import Counter
from typing import List
import numpy as np
import math
import pandas as pd

# Define a class to store a single sentiment example
class SentimentExample:
    def __init__(self, words, label):
        self.words = words
        self.label = label

    def __repr__(self):
        return repr(self.words) + "; label=" + repr(self.label)

    def __str__(self):
        return self.__repr__()


# Reads sentiment examples in the format [0 or 1]<TAB>[raw sentence]; tokenizes and cleans the sentences.
def read_sentiment_examples(df):
    """
    Takes a DataFrame and returns a list of (review, voted_up) tuples.
    Assumes DataFrame has columns 'review' and 'voted_up'.
    """
    return list(zip(df['review'], df['voted_up']))

testData = pd.read_excel('steam-review-classification/all_steam_game_reviews_english.xlsx')

print(read_sentiment_examples(testData))
