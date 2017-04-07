from django.test import TestCase
from ordinaryPython36.Supporting.services import ArticleService, SimilarArticleListService, FeedService
from ordinaryPython36.Supporting.aggregator import Aggregator
from ordinaryPython36.Supporting.recsys import ContentEngine, KNN
from ordinaryPython36.Supporting.generators.user_interaction_generator import UserArticleInteractionGenerator
import time
from ordinaryPython36.Supporting.text_summarizer import FrequencySummarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from ordinaryPython36.models import Article, SimilarArticleList, UserArticleInteraction
from sklearn.metrics.pairwise import linear_kernel
from collections import namedtuple
import random
from django.utils import timezone
from datetime import timedelta

# Create your tests here.


class AggregatorTestCase():
    def test_aggregator(self, category_id=1):
        a = Aggregator()
        a.aggregate(category_id)


class ModelsTestCase:
    def get_article_text_column(self, category_id=1):
        #a = ArticleService().get_articles_by_category_id(category_id)
        #print(a.values('id', 'title')[0]['id']) # print id of first dict
        #print (a.values_list('title', flat=True)) #.values('title'))

        article_list_of_dicts = ArticleService().get_articles_by_category_id_including_children(
            category_id).values('id', 'text').order_by('id')
        artcle_ids = article_list_of_dicts.values_list('id', flat=True)
        artcle_texts = article_list_of_dicts.values_list('title', flat=True)
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

        tfidf_matrix = tf.fit_transform(artcle_texts)

        #print(artcle_ids)
        #print(artcle_texts)

        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        for idx in range(0, article_list_of_dicts.count()): #article_dic instead idx and row
            #article_ids[idx] - current article id

            similar_indices = cosine_similarities[idx].argsort()[:-12:-1] #get indices of 10 most similar items
            #similar_items = [(cosine_similarities[idx][i], artcle_ids[i]) for i in similar_indices]
            print(artcle_ids[idx])
            similar_articles = []
            for i in similar_indices:
                if cosine_similarities[idx][i] < 0.05:
                    break
                if i == idx:
                    continue

                similar_articles.append(str(artcle_ids[int(i)]))
            SimilarArticleList.objects.create(
                similar_articles=', '.join(similar_articles), article=Article.objects.get(id=artcle_ids[idx]))
            # First item is the item itself, so remove it.
            # This 'sum' is turns a list of tuples into a single tuple: [(1,2), (3,4)] -> (1,2,3,4)
            #flattened = sum(similar_items[1:], ())
            #print(flattened)
            #print(artcle_ids[idx])
            #print(similar_items[1:])
            #print("--------------")


class ArticleServiceTestCase:
    def get_articles_by_category_id_including_children_sum(self):
        sum = 0
        for i in range(13):
            if i < 3: continue
            sum += ArticleService().get_articles_by_category_id_including_children(i).count()
        print(sum)

class PeriodicTaskPerformer:
    def performTasks(self):
        beg = 32
        end = 3
        id = beg

        a = Aggregator()
        while id >= end:
            a.aggregate(category_id=id)
            id -= 1

        contentEngine = ContentEngine()
        for i in range(14):
            if i < 3: continue
            contentEngine.train(i)
#--------#--------#--------#--------#--------#--------#--------#--------#--------#--------#--------
#print(SimilarArticleListService().get_similar_articles(158))

#print(SimilarArticleListService().get_similiarity_list(article_id=158))
#resulting = [1, 2, 3, 4] + list(set([3, 4, 5]) - set([1, 2, 3, 4]))
#print(resulting)

class ReadRatingsTest:
    def read_ratings(self, flname):
        Rating = namedtuple("Rating", ["user_id", "movie_id", "rating", "timestamp"])
        ratings = []
        with open(flname) as fl:
            for ln in fl:
                user_id, movie_id, rating, timestamp = ln.strip().split("::")
                ratings.append(Rating(user_id=int(user_id) - 1,
                             movie_id=int(movie_id) - 1,
                             rating=float(rating),
                             timestamp=int(timestamp)))
        return ratings



"""
rr = ReadRatingsTest().read_ratings("ordinaryPython36/ml-1m/ratings.dat") #  actual user_ids and movie-ids are +1
knn = KNN()
training, testing, users_train_dict, users_predict_dict = knn.get_data(rr, 200, 3)
user_recommended_movies_dict = knn.predict(training, testing)
for user in user_recommended_movies_dict.keys():
    print(users_train_dict[user], user, user_recommended_movies_dict[user])
# for r in rr:
#    print(r.user_id, r.movie_id, r.rating, r.timestamp)
"""

#uaig = UserArticleInteractionGenerator()
#uaig.generate(user_id=5, category_id=11, percentage_of_newest_articles=0.5)

#PeriodicTaskPerformer().performTasks()

"""
article = Article.objects.get(id=96)
similar_articles = ContentEngine().predict(article)
for i in similar_articles:
    print(i)
"""

"""
fs = FrequencySummarizer()
for a in Article.objects.all():
    a.summary = fs.summarize(a.text.replace("\n"," "), 5)
    a.save()
"""