from ordinaryPython36.models import Category, Feed, Article, SimilarArticleList, UserProfile, UserArticleInteraction
from itertools import chain

class UserProfileService:
    def addUserProfile(self, uid, name=None, email=None, picture=None):
        userProfile = UserProfile(uid=uid, name=name, email=email, picture=picture)
        userProfile.save()


class UserArticleInteractionService:
    def add_article_to_user_history(self, date_accessed, user, article):
        uai = UserArticleInteraction(date_accessed=date_accessed, user=user, article=article)
        uai.save()


class CategoryService:
    def addcategory(self, name):
        category = Category(name=name)
        category.save()

    def get_root_categories(self):
        return Category.objects.filter(parent=None)

    def getAll(self):
        return Category.objects.all()

    def getCategoriesByName(self, names=[]):
        return Category.objects.filter(name__in=names)

    def getParentWithChildren(self, category):
        child_categories = Category.objects.filter(parent=category)
        parent_category = Category.objects.get(id=category)
        return list(chain(parent_category, child_categories))


class FeedService:
    def addfeed(self, url, name=None, description=None):
        feed = Feed(url=url, name=name, description=description)
        feed.save()

    def get_feeds_by_category_id(self, category_id):
        return Feed.objects.filter(category_id__exact=category_id)

    def get_child_feeds_by_category_id(self, category_id):
        return Feed.objects.filter(category__parent_id__exact=category_id)

    def get_feeds_by_category_id_including_children(self, category_id):
        child_feeds = self.get_child_feeds_by_category_id(category_id)
        root_feeds = self.get_feeds_by_category_id(category_id)
        return list(chain(child_feeds, root_feeds))


class ArticleService:
    def get_articles_by_category_id(self, root_category_id):
        feeds = FeedService().get_feeds_by_category_id(root_category_id)
        return Article.objects.filter(feed_id__in=feeds)

    def get_articles_by_category_id_including_children(self, root_category_id):
        feeds = FeedService().get_feeds_by_category_id_including_children(root_category_id)
        return Article.objects.filter(feed_id__in=feeds)

    # return dictionary mapping article indices with article ids
    def get_newest_articles_in_category(self, category_id, size):
        articles = self.get_articles_by_category_id_including_children(
            root_category_id=category_id).order_by('-date')[:size]
        idx = 0
        idx_article_id_dict = dict()
        for article in articles:
            idx_article_id_dict[idx] = article.id
            idx += 1
        return idx_article_id_dict

        # return dictionary mapping article indices with article ids

    def get_newest_articles_in_category_by_percentage(self, category_id, percentage):
        tmp_art = self.get_articles_by_category_id_including_children(
            root_category_id=category_id).order_by('-date')
        size = int(percentage * tmp_art.count())
        articles = tmp_art[:size]
        idx = 0
        idx_article_id_dict = dict()
        for article in articles:
            idx_article_id_dict[idx] = article.id
            idx += 1
        return idx_article_id_dict


class SimilarArticleListService:
    def get_similar_articles(self, article_id):
        try:
            similiarity_list = SimilarArticleList.objects.get(article_id=article_id).similar_articles.split(', ')
            return Article.objects.filter(pk__in=similiarity_list)
        except SimilarArticleList.DoesNotExist:
            return None
        except SimilarArticleList.MultipleObjectsReturned:
            return None

        return None

    def get_similiarity_list(self, article_id):
        try:
            return SimilarArticleList.objects.get(article_id=article_id)
        except SimilarArticleList.DoesNotExist:
            return None
        except SimilarArticleList.MultipleObjectsReturned:
            return None

        return None

    def is_similiarity_ist_contained_for_article(self, article_id):
        try:
            SimilarArticleList.objects.get(article_id=article_id)
            return True
        except SimilarArticleList.DoesNotExist:
            return False
        except SimilarArticleList.MultipleObjectsReturned:
            return False

        return False