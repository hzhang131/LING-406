import string
import csv
import pandas
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score 

dataset = pandas.read_csv('pos-eng-5000.data.csv')
print(dataset.to_numpy())
