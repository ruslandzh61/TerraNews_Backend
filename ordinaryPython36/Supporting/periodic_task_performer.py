from ordinaryPython36.Supporting.aggregator import Aggregator
from ordinaryPython36.Supporting.recommendation_engine.recsys import ContentEngine, KNN
from ordinaryPython36.models import Category


class PeriodicTaskPerformer:

    def perform_all_tasks(self):
        self.perform_aggregation()
        self.perform_article_similarity_calculation()
        self.perform_user_similarity_calculation_in_category()

    # since an article directly belongs only to one feed and category and indirectly -
    # to two categories (child and parent), aggregate content in the following order:
    # 1. for child categories
    # 2. then for parent categories,
    def perform_aggregation(self):
        a = Aggregator()
        for category in Category.objects.all().order_by('-id'):
            a.aggregate(category_id=category.id)

    def perform_article_similarity_calculation(self):
        contentEngine = ContentEngine()
        for i in range(14):
            if i < 3: continue
            contentEngine.train(i)

    def perform_user_similarity_calculation_in_category(self):
        for category in Category.objects.all():
            category_id = category.id
            knn = KNN(category_id)
            performed = knn.perform_user_similarity_calculation()
            if performed:
                print("user similarity calculation performed on category", category_id)
            else:
                print("user similarity calculation not performed on category", category_id)

# 350 userToCategories: 5 (neighbor) * 10
# 50 categories (10) * users (7) = 70