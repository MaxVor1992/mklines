import pickle
from sklearn import datasets
import sklearn
# from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
import pandas as pd
import distance
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

data = pickle.load(open("data.txt", "rb"))
res = []
inx = 0
urls = []
for k in data:
    inx += 1
    for item in data[k]:
        urls.append(item[0].url)
        res.append(item[0].url + " | " + str(inx))
file = open('urls.txt', "w")
file.write("\n".join(urls))
file.close()
# print(res)
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(res)
# # print(res)
# df = pd.DataFrame(res)
# print(df)
model = KMeans(n_clusters=3)
model.fit(X)
# model = AffinityPropagation()
# model.fit(df)
print("Top terms per cluster:")
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
for i in range(3):
    print("Cluster %d:" % i),
    for ind in order_centroids[i, :10]:
        print(' %s' % terms[ind]),
while 1:
    print("prediction:")
    s = input("enter word >>")
    Y = vectorizer.transform([s])
    print(model.predict(Y))
