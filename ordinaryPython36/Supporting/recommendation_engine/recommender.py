from ordinaryPython36.Supporting.services import UserArticleInteractionService, SimilarArticleListService
from ordinaryPython36.models import Article, UserArticleInteraction
from django.utils import timezone
from datetime import timedelta
from ordinaryPython36.models import UserSimilarityInCategory
from django.db.models import Count

class UserCategoryRecommendationEngine:

    # user_id and category_id for which make recommendation,
    def __init__(self, user_id, category_id, datetime_begin=None):
        self.user_id = user_id
        self.category_id = category_id
        if datetime_begin is None:
            self.datetime_begin = timezone.now() - timedelta(days=3)

    def make_recommendations(self, size=30):
        result = list()
        similar_users_articles = self.__get_articles_of_similar_users__(int(size/2))
        top_articles = self.__get_top_articles__(int(size/3))
        similar_articles = self.__get_similar_articles__(int(size/6))
        result.extend(similar_users_articles)
        result.extend(similar_articles)
        result.extend(top_articles)
        return list(set(result))
    # get n(size) articles for a given user(user_id) and category(category_id),
    # accessed by similar users in the past n(days) days

    def __get_articles_of_similar_users__(self, size):
        similar_users = []
        for item in UserSimilarityInCategory.objects.filter(
                user_category__user=self.user_id, user_category__category=self.category_id).order_by(
            '-similarity_ratio').values('similar_user'):
            similar_users.append(item['similar_user'])

        articles = UserArticleInteractionService().get_users_history_in_category(
            users=similar_users, category=self.category_id).filter(
            article__date__gt=self.datetime_begin).values('article').annotate(
            itemcount=Count('article')).order_by('-itemcount').values('article', 'itemcount')
        result = []
        for idx, a in enumerate(articles):
            if idx >= size:
                break
            #print(a['article'], a['itemcount'])
            result.append(Article.objects.get(id=a['article']))
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
            if similar_articles is not None:
                similar_article = similar_articles.first()
            else:
                continue
            result.append(similar_article)
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