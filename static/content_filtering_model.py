import pandas as pd
import numpy as np
import re
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
import pickle
from sklearn.metrics import roc_curve
import datetime


class Model:
	
	def __init__(self):
		self.model = LogisticRegression()
		self.tfidf = TfidfVectorizer()
		self.threshold=None

	def fit(self, X, y):
		self.X = self.tfidf.fit_transform(X)
		self.y = y
		
		self.model.fit(self.X, self.y)
		self._get_optimal_threshold()
		filename = 'data/filtering_model.pkl'
		pickle.dump(self, open(filename, 'wb'))

	def _get_optimal_threshold(self):
		fpr, tpr, threshold = roc_curve(self.y, self.predict_proba(self.X, threshold=True)[:,1])
		i = np.arange(len(tpr)) 
		roc = pd.DataFrame({'tf' : pd.Series(tpr-(1-fpr), index=i), 'threshold' : pd.Series(threshold, index=i)})
		roc_t = roc.loc[(roc.tf-0).abs().argsort()[:1]]
		self.threshold = list(roc_t['threshold'])[0]
		print('Best Threshold: {}'.format(self.threshold))

	def predict(self, X):
		X = self.tfidf.transform(X)
		predictions = (self.predict_proba(X)[:,1] > self.threshold)*1
		return predictions

	def predict_proba(self, X, threshold=False):
		# get_optimal_threshold method calls upon predict_proba. 
		if threshold == False:
			X = self.tfidf.transform(X)
		else:
			X = self.X

		predictions = self.model.predict_proba(X)
		return predictions

	def score(self, X, y):
		X = self.tfidf.transform(X)
		score = self.model.score(X, y)
		return score

def main():
	d = datetime.date.today()
	try:
		df = pd.read_csv('data/pipeline_data/offensive_content{}.csv'.format(d.strftime('%y%m%d'))).drop(['Unnamed: 0'],axis=1)
	except:
		df = pd.read_csv('data/pipeline_data/offensive_content.csv').drop(['Unnamed: 0'],axis=1)
	X = df['text']
	y = df['offensive']

	X_train, X_test, y_train, y_test = train_test_split(
	    X,y, train_size=0.75, shuffle=True, stratify=y)
	
	model = Model()
	model.fit(X_train, y_train)
	print('Accuracy score {}'.format(model.score(X_test, y_test)))


if __name__ == '__main__':
	main()
