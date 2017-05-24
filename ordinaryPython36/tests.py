from django.test import TestCase
from ordinaryPython36.Supporting.services import ArticleService, UserArticleInteractionService
from ordinaryPython36.Supporting.aggregator import Aggregator
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from ordinaryPython36.models import Article, SimilarArticleList
from sklearn.metrics.pairwise import linear_kernel
from django.utils import timezone
from datetime import timedelta
from ordinaryPython36.Supporting.periodic_task_performer import PeriodicTaskPerformer
from ordinaryPython36.models import UserToCategory, UserSimilarityInCategory, UserProfile, Category,\
    UserArticleInteraction, Feed, Channel
from django.db.models import Count
from ordinaryPython36.Supporting.generators.user_interaction_generator import UserArticleInteractionGenerator
from ordinaryPython36.Supporting.recommendation_engine.recommender import UserCategoryRecommendationEngine
from ordinaryPython36.Supporting.recommendation_engine.recsys import ContentEngine
from ordinaryPython36.Supporting.generators.datetime_generator import DatetimeGenerator
from ordinaryPython36.Supporting.generators.user_interaction_generator import UserArticleInteractionGenerator
import requests
from ordinaryPython36.Supporting.serializers import *
from itertools import chain

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

class GeneratorTestCase:
    def generate(self):
        for user in UserProfile.objects.all():
            uaig = UserArticleInteractionGenerator()
            for j in range(3, 14):
                perc = (5 + j) / 300.0
                uaig.generate(user_id=user.id, category_id=j, percentage_of_newest_articles=perc)

#--------#--------#--------#--------#--------#--------#--------#--------#--------#--------#--------
#print(SimilarArticleListService().get_similar_articles(158))

#print(SimilarArticleListService().get_similiarity_list(article_id=158))
#resulting = [1, 2, 3, 4] + list(set([3, 4, 5]) - set([1, 2, 3, 4]))
#print(resulting)

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



# get  articles in the last 7 days most frequently accessed by the most similar users
#print(articles)
#article_set = list(article.article for article in articles)#filter(date__gte=datetime_begin).count())
#    print(article.itemcount)
#print(article_set)

# car = CategoryArticlesRecommender()
# for i in car.get_recommended(5, 11, 10):
#    print(i)
#PeriodicTaskPerformer().perform_all_tasks()
#PeriodicTaskPerformer().perform_user_similarity_calculation_in_category()
#

# date_begin = timezone.now() - timedelta(days=10)
#
# result = UserCategoryRecommendationEngine(user_id=5, category_id=11).make_recommendations()
# for a in result:
#     print(a)
# print(len(result))

# result = list(UserArticleInteraction.objects.filter(article__feed__category__exact=11,
#            article__date__gt=date_begin).values('article').annotate(itemcount=Count('article')).order_by(
#     '-itemcount').values('article', 'itemcount'))
# for i in result:
#     print(i['article'], i['itemcount'])
#PeriodicTaskPerformer().perform_article_similarity_calculation()

"""
PeriodicTaskPerformer().perform_aggregation()
PeriodicTaskPerformer().perform_article_similarity_calculation()
uai = UserArticleInteractionGenerator()
for category in Category.objects.all():
    for user in UserProfile.objects.all():
        uai.generate(category_id=category.id, user_id=user.id, percentage_of_newest_articles=0.2)
PeriodicTaskPerformer().perform_user_similarity_calculation_in_category()
"""
#r = requests.post('http://localhost:8000/newsfeed/api/v1/users', data= {'uid':'6jKNcXYvIPUjXnsLvabsvBKySot2'})
#r = requests.put("http://somedomain.org/endpoint", data=payload)

"""
user_channel = Channel.objects.get(id=20)
serializer = ChannelSerializer(user_channel)
response = requests.delete('http://localhost:8000/newsfeed/api/v1/channels', data=serializer.data)
"""

#UserProfile.objects.create(uid='fdgdfffgsdfgb', name='test for default channels')

"""
uai = UserArticleInteractionGenerator()
for category in Category.objects.all():
    for user in UserProfile.objects.all():
        uai.generate(category_id=category.id, user_id=user.id, percentage_of_newest_articles=0.2)
"""

"""
article = Article.objects.get(id=96)
similar_articles = ContentEngine().predict(article)
for i in similar_articles:
    print(i)
"""

"""
Channel.objects.create(name='Tech', is_system_channel=False, user_id=25)
ChannelPublisher.objects.create(following_channel_id=38, category_id=3)
ChannelPublisher.objects.create(following_channel_id=38, category_id=5)
ChannelPublisher.objects.create(following_channel_id=38, category_id=7)
"""

"""
Collection.objects.create(name="Tech companies", user_id=25)
CollectionArticle.objects.create(collection_id=2, article_id=1635)
CollectionArticle.objects.create(collection_id=2, article_id=1629)
"""

"""
for article in SimilarArticleList.objects.all():
    if article.similar_articles.startswith(', '):
        article.similar_articles = article.similar_articles[2:]
        article.save()
"""
class ContEngine:
    def train(self):
        date = timezone.now()
        date -= timedelta(days=21)
        article_list_of_dicts = ArticleService().get_articles_by_category_id_including_children(
            3).filter(date__gt=date).values('id', 'text').order_by('id')[:5]
        if article_list_of_dicts.count() < 1:
            return

        artcle_ids = article_list_of_dicts.values_list('id', flat=True)
        artcle_texts = article_list_of_dicts.values_list('text', flat=True)
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

        #tf.fit()
        #count_vectorizer = CountVectorizer()

        tfidf_matrix = tf.fit_transform(artcle_texts)
        print(tf.shape)
        print("----------------------")
        print("dghfhdfghf")
        print(tfidf_matrix)

#a = Aggregator()
#a.aggregate(category_id=11)


#ContentEngine(11).train()

#generate short term interactions: last week, take last 500 from tech (0.2), - 50 inter
#generate long term interactions: last month, take last 2000 from tech (0.8) - 200 inter
#user interacts with every 10th article


#generate for 10 days
#last 0.4 articles ~ 1000 articles
#identify similar user within last 7 days
# 5 closest users
#make recommendations for the last day
#begin date 22 May

"""
uai = UserArticleInteractionGenerator()
for user in UserProfile.objects.all():
    category_id = 3
    while category_id < 14:
        uai.generate(category_id=category_id, user_id=user.id, percentage_of_newest_articles=0.2, short_time=True)
        category_id += 1
"""

#PeriodicTaskPerformer().perform_user_similarity_calculation_in_category()
category_id = 3
while category_id < 14:
    Aggregator().aggregate(3)
    category_id += 1

"""
#ContEngine().train()
#feed=Feed.objects.get(id=13)
#Article.objects.create(title="title", url="http://idolosol.com/images/fd-1.jpg", text='text', feed=feed)
"""

"""
date_from = timezone.now()
date_from -= timedelta(days=7)
his = UserArticleInteractionService().get_user_history_in_category(user=25,category=11, date_from=date_from)
for a in his:
    print(a.date_accessed)"""

"""
date_from = timezone.now()
date_from -= timedelta(days=7)
similar_users = []
for item in UserSimilarityInCategory.objects.filter(
        user_category__user=25, user_category__category=11).order_by(
    '-similarity_ratio').values('similar_user'):
    similar_users.append(item['similar_user'])

articles = UserArticleInteractionService().get_users_history_in_category(
            users=similar_users, category=11).filter(
            article__date__gt=date_from).values('article').annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')

result = []
for idx, a in enumerate(articles):
    if idx >= 15:
        break
    print(a['article'], a['itemcount'])
    result.append(Article.objects.get(id=a['article']))
"""

"""
date_from = timezone.now()
date_from -= timedelta(days=7)

similar_users = []
for item in UserSimilarityInCategory.objects.filter(
        user_category__user=25, user_category__category=11).order_by(
    '-similarity_ratio').values('similar_user'):
    similar_users.append(item['similar_user'])
user_articles = UserArticleInteractionService().get_user_history_in_category(
    user=25, category=11, date_from=date_from).values('article_id')
articles = UserArticleInteractionService().get_users_history_in_category(
    users=similar_users, category=11).filter(
    article__date__gt=date_from).values(
    'article').exclude(article__in=user_articles).values('article')
articles_sorted = articles.annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')
similar_user_set = Article.objects.filter(id__in=articles)
print(similar_user_set.count())
"""
"""
article_ids = [26000, 26001, 26002]
aa = Article.objects.filter(id__in=article_ids)
for a in aa:
    print(a.id)
fg = [26001, 2, 4]
for i in fg:
    print(aa.filter(id=i).exists())"""

"""
article_ids = [26000, 26001, 26002]
a=Article.objects.filter(id__in=article_ids)
fg = [26005, 26006]
b=Article.objects.filter(id__in=fg)
c =a | b
print(c.count())
"""

#UserArticleInteraction.objects.create(user_id=25, article_id=26959)