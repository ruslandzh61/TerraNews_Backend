from django.test import TestCase
from ordinaryPython36.Supporting.services import ArticleService, SimilarArticleListService
from ordinaryPython36.Supporting.aggregator import Aggregator, ContentEngine
from ordinaryPython36.models import *
import time
from ordinaryPython36.Supporting.text_summarizer import FrequencySummarizer
# Create your tests here.


"""class AggregatorTestCase():
    def test_aggregator(self, category_id=1):
        a = Aggregator()
        a.aggregate(category_id)


class ModelsTestCase:
    def get_article_text_column(self, category_id=1):
        #a = ArticleService().get_articles_by_category_id(category_id)
        #print(a.values('id', 'title')[0]['id']) # print id of first dict
        #print (a.values_list('title', flat=True)) #.values('title'))

        article_list_of_dicts = ArticleService().get_articles_by_category_id(category_id).values('id', 'text').order_by('id')
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
            #print("--------------")"""


#a = Aggregator()
#a.aggregate(category_id=1)

"""article = Article.objects.get(id=96)
similar_articles = ContentEngine().predict(article)
for i in similar_articles:
    print(i)"""
fs = FrequencySummarizer()
for a in Article.objects.all():
    a.summary = fs.summarize(a.text.replace("\n"," "), 5)
    a.save()