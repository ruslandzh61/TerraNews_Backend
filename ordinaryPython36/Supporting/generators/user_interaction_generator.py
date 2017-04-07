from ordinaryPython36.models import Article, UserArticleInteraction, UserProfile
import random
from ordinaryPython36.Supporting.generators.datetime_generator import DatetimeGenerator
from ordinaryPython36.Supporting.services import ArticleService


class UserArticleInteractionGenerator():
    # % of newest articles should be defined as decimal number in range [0..1]
    def generate(self, user_id, category_id, percentage_of_newest_articles):
        if percentage_of_newest_articles <= 0.0:
            return
        user = UserProfile.objects.get(id=user_id)
        time_generator = DatetimeGenerator()
        article_service = ArticleService()
        idx_article_id_dict = article_service.get_newest_articles_in_category_by_percentage(
            category_id, percentage_of_newest_articles)
        dataset_size = len(idx_article_id_dict)
        sample_size = int(dataset_size / 10)
        sampled_indices = random.sample(range(dataset_size), sample_size)

        for idx in sampled_indices:
            article_id = idx_article_id_dict[idx]
            article = Article.objects.get(id=article_id)
            date_accessed = time_generator.generate(article.date)
            UserArticleInteraction.objects.create(user=user, article=article, date_accessed=date_accessed)
            print("user article interaction generated", idx, article_id, date_accessed)
