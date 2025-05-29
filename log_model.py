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
    Takes a DataFrame and returns a list of (words, voted_up) tuples.
    Tokenizes and lowercases the review text.
    Assumes DataFrame has columns 'review' and 'voted_up'.
    """
    examples = []
    for review, voted_up in zip(df['review'], df['voted_up']):
        # Basic preprocessing: lowercase and split on whitespace
        words = str(review).lower().split()
        examples.append((words, bool(voted_up)))
    return examples

testData = pd.read_excel('all_steam_game_reviews_english.xlsx')

trainEx = read_sentiment_examples(testData)

n_pos = 0
n_neg = 0
for ex in trainEx:
    if ex[1] == True:
        n_pos += 1
    else:
        n_neg += 1
        
print(f"Number of positive reviews: {n_pos}")
print(f"Number of negative reviews: {n_neg}")
