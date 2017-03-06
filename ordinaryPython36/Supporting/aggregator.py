import feedparser
import urllib.error
from ordinaryPython36.Supporting.services import ArticleService, FeedService, SimilarArticleListService
from newspaper import Article as newspaperArticle
from ordinaryPython36.models import Feed, Article, SimilarArticleList
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class Aggregator:
    def aggregate(self, category_id):
        fds = FeedService()
        feedmodels = fds.get_feeds_by_category_id(category_id)
        for feedmodel in feedmodels:
            try:
                feed = feedparser.parse(feedmodel.url)
                for item in feed.entries:
                    # check if it is already contained in the database
                    if Article.objects.filter(url=item.link).count() > 0:
                        continue

                    # parsing
                    parser = newspaperArticle(item.link)
                    parser.download()
                    parser.parse()

                    # add to database
                    Article.objects.create (
                        url=item.link, title=parser.title,
                        text=parser.text, date=parser.publish_date,
                        top_image=parser.top_image, feed=feedmodel)

                    # Tagging
                    # parser.nlp()
                    # print(article.keywords)

                    # sentiment analysis
                    #t = TextBlob(article.text)
                    #print(t.sentiment.polarity)
            except urllib.error.URLError:
                print("Incorrect URL specified")
                continue


class ContentEngine:
    def train(self, category_id):
        article_list_of_dicts = ArticleService().get_articles_by_category_id(category_id).values('id', 'text').order_by(
            'id')
        artcle_ids = article_list_of_dicts.values_list('id', flat=True)
        artcle_texts = article_list_of_dicts.values_list('title', flat=True)
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

        tfidf_matrix = tf.fit_transform(artcle_texts)

        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        for idx in range(0, article_list_of_dicts.count()):  # article_dic instead idx and row
            # article_ids[idx] - current article id
            """x = numpy.array([1.48,1.41,0.0,0.1])
                        print x.argsort()
                        [2 3 1 0]"""
            similar_indices = cosine_similarities[idx].argsort()[:-12:-1]  # get indices of 10 most similar items
            similar_articles = []
            for i in similar_indices:
                if cosine_similarities[idx][i] < 0.05:
                    break
                if i == idx:
                    continue

                similar_articles.append(str(artcle_ids[int(i)]))
            SimilarArticleList.objects.create(
                similar_articles=', '.join(similar_articles), article=Article.objects.get(id=artcle_ids[idx]))

    def predict(self, article):
        return SimilarArticleListService().get_similar_articles(article)
