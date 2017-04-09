from ordinaryPython36.Supporting.services import UserArticleInteractionService
from ordinaryPython36.models import Article
from django.utils import timezone
from datetime import timedelta
from ordinaryPython36.models import UserSimilarityInCategory
from django.db.models import Count

class CategoryRecommendationEngine:

    # get n(size) articles for a given user(user_id) and category(category_id),
    # accessed by similar users in the past n(days) days
    def get_articles_of_similar_users(self, user_id, category_id, days, size):
        similar_users = []
        for item in list(UserSimilarityInCategory.objects.filter(user_category__user=user_id, user_category__category=category_id).values(
            'similar_user', 'similarity_ratio')):
            similar_users.append(item['similar_user'])

        datetime_begin = timezone.now() - timedelta(days=days)
        article_interactions = UserArticleInteractionService().get_users_history_in_category(
            users=similar_users, category=11).filter(
            article__date__gt=datetime_begin).annotate(itemcount=Count('article')).order_by('-itemcount')#.values('article')
        result = []
        for ai in article_interactions:
            result.append(Article.objects.get(id=ai.article_id))
        return result[:size]