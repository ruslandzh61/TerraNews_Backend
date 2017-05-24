from django.db import models
from django.core.validators import int_list_validator
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
import django.utils.timezone
# Create your models here.

class UserProfile(models.Model):
    uid = models.TextField(null=False, unique=True)
    name = models.TextField(max_length=100, default="")
    email = models.EmailField(null=True)
    picture = models.URLField(null=True)

    def __str__(self):
        return str(self.id)

class Publisher(models.Model):
    name = models.TextField(max_length=100, null=False)
    description = models.TextField(null=True)
    logo = models.URLField(null=True)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.TextField(max_length=100, null=False)
    parent = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.TextField(max_length=100, null=False)
    parent = models.ForeignKey('self', null=True)  # self reference

    def __str__(self):
        return self.name


class Feed(models.Model):
    url = models.URLField()
    name = models.TextField(max_length=100, null=True)
    description = models.TextField(null=True)
    last_updated = models.DateTimeField(null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True)
    added_by_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.category.name + ' : ' + self.publisher.name + ' : ' + self.url


class Article(models.Model):
    url = models.URLField(default="", max_length=2000)  # default max length=200
    top_image = models.URLField(max_length=2000, null=True)
    title = models.TextField(default="")
    date = models.DateTimeField(null=True)
    text = models.TextField(default="")
    summary = models.TextField(default="")
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class UserToCategory(models.Model):
    user = models.ForeignKey(UserProfile, null=False)
    category = models.ForeignKey(Category, null=False)
    unique_together = ('user', 'category')


class UserSimilarityInCategory(models.Model):
    user_category = models.ForeignKey(UserToCategory, null=False)
    similar_user = models.ForeignKey(UserProfile, null=False)
    similarity_ratio = models.FloatField(null=False, validators=[
            MaxValueValidator(1.0), MinValueValidator(0.0)])
    unique_together = ('user_category', 'similar_user')

    def __str__(self):
        return str(self.user_category.id) + ": " + str(self.similar_user.id) + ": " + str(self.similarity_ratio)

"""
class LongUserSimilarityInCategory(models.Model):
    user_category = models.ForeignKey(UserToCategory, null=False)
    similar_user = models.ForeignKey(UserProfile, null=False)
    similarity_ratio = models.FloatField(null=False, validators=[
            MaxValueValidator(1.0), MinValueValidator(0.0)])
    unique_together = ('user_category', 'similar_user')

    def __str__(self):
        return str(self.user_category.id) + ": " + str(self.similar_user.id) + ": " + str(self.similarity_ratio)
"""


class SimilarArticleList(models.Model):
    similar_articles = models.TextField(validators=int_list_validator(
        sep=', ', message=None, code='invalid', allow_negative=False))
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.article_id) + ": " + self.similar_articles


class UserArticleInteraction(models.Model):
    date_accessed = models.DateTimeField(null=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.user) + str(self.article)


class Channel(models.Model):
    name = models.TextField(max_length=100, default="")
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    is_system_channel = models.BooleanField(null=False)


class ChannelFeed(models.Model):
    following_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)


class ChannelCategory(models.Model):
    following_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)


class ChannelPublisher(models.Model):
    following_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)


class TagChannel(models.Model):
    tag = models.TextField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)


class Collection(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    name = models.TextField(max_length=100, default="")
    description = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)


class CollectionArticle(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)


class OfflineArticle(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    date_offlined = models.DateTimeField(auto_now_add=True, blank=True)
    date_removed = models.DateTimeField(null=True)
