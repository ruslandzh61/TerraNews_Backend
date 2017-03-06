from ordinaryPython36.models import Category, Feed, Article, SimilarArticleList

class CategoryService:
    def addcategory(self, name):
        category = Category(name=name)
        category.save()

class FeedService:
    def addfeed(self, url, name=None, description=None):
        feed = Feed(url=url, name=name, description=description)
        feed.save()
    def get_feeds_by_category_id(self, category_id):
        return Feed.objects.filter(category_id__exact=category_id)

class ArticleService:
    def get_articles_by_category_id(self, category_id):
        return Article.objects.filter(feed__category_id__exact=category_id)

class SimilarArticleListService:
    def get_similar_articles(self, article):
        similar_article_list = SimilarArticleList.objects.get(article_id=article).similar_articles.split(', ')

        return Article.objects.filter(pk__in=similar_article_list)