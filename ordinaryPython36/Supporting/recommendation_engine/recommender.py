from ordinaryPython36.Supporting.services import UserArticleInteractionService, SimilarArticleListService
from ordinaryPython36.models import Article, UserArticleInteraction
from django.utils import timezone
from datetime import timedelta
from ordinaryPython36.models import UserSimilarityInCategory
from django.db.models import Count
from ordinaryPython36.Supporting.recommendation_engine.recsys import ContentEngine
from collections import namedtuple
class UserCategoryRecommendationEngine:

    # user_id and category_id for which make recommendation,
    def __init__(self, user_id, category_id, datetime_begin):
        self.user_id = user_id
        self.category_id = category_id

        self.datetime_begin = datetime_begin

    def make_recommendations(self, size=30):
        result = list()
        #similar_users_articles = self.__get_articles_of_similar_users__(int(size/2))
        top_articles = self.__get_top_articles__(int(size/3))
        similar_articles = self.__get_similar_articles__(int(size/6))

        #result.extend(similar_users_articles)
        #result.extend(top_articles)
        result.extend(similar_articles)
        for r in result:
            print(r.title)
        return list(set(result))
    # get n(size) articles for a given user(user_id) and category(category_id),
    # accessed by similar users in the past n(days) days

    def __get_articles_of_similar_users__(self, size):
        similar_users = []
        for item in UserSimilarityInCategory.objects.filter(
                user_category__user=self.user_id, user_category__category=self.category_id).order_by(
            '-similarity_ratio').values('similar_user'):
            similar_users.append(item['similar_user'])
        user_interactions = UserArticleInteractionService().get_user_history_in_category(
            user=self.user_id, category=self.category_id, date_from=self.datetime_begin).values('id')
        articles = UserArticleInteractionService().get_users_history_in_category(
            users=similar_users, category=self.category_id).filter(
            article__date__gt=self.datetime_begin).exclude(
            id__in=user_interactions).values('article').annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')

        # articles to exclude
        user_articles = UserArticleInteractionService().get_user_history_in_category(
            user=self.user_id, category=self.category_id, date_from=self.datetime_begin).values('article_id')
        # articles of similar users without user's articles
        articles = UserArticleInteractionService().get_users_history_in_category(
            users=similar_users, category=self.category_id).filter(
            article__date__gt=self.datetime_begin).values(
            'article').exclude(article__in=user_articles).annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')
        #articles_sorted = articles.annotate(itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')
        result = []

        for idx, a in enumerate(articles):
            if idx >= size:
                break
            #print(a['article'], a['itemcount'])
            result.append(Article.objects.get(id=a['article']))

        #user_article_set = Article.objects.filter(id__in=user_articles)
        #similar_user_article_set = Article.objects.filter(id__in=articles)
        #recommended = ContentEngine(category_id=11).train()

        return result

    # get similar articles
    def __get_similar_articles__(self, size):
        result = []
        articles = UserArticleInteraction.objects.filter(article__feed__category__exact=self.category_id,
              user_id=self.user_id).order_by('-date_accessed').values('article')
        for idx, a in enumerate(articles):
            if idx >= size:
                break
            similar_articles = SimilarArticleListService().get_similar_articles(a['article'])
            for sim_idx, similar_article in enumerate(similar_articles):
                if sim_idx > 1:
                    break
                #print("similar: ", similar_articles)
                #print(Article.objects.get(id=a['article']), ' ::: ', similar_article)
                #print('---------------')
                result.append(similar_article)
                #print(a['article'])

            #print(Article.objects.get(id=a['article']), similar_article)

        return result

    def __get_top_articles__(self, size):
        top_articles = []
        result = UserArticleInteraction.objects.filter(article__feed__category__exact=self.category_id,
                        article__date__gt=self.datetime_begin).values('article').annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article')
        for idx, a in enumerate(result):
            if idx >= size:
                break
            #print(a['article'], a['itemcount'])
            top_articles.append(Article.objects.get(id=a['article']))
            print(Article.objects.get(id=a['article']))
        return top_articles