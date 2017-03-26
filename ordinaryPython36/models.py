from django.db import models
from django.core.validators import int_list_validator


# Create your models here.

class Publisher(models.Model):
    name = models.TextField(max_length=100, null=False)
    description = models.TextField(null=True)
    logo = models.ImageField(null=True)

class Region(models.Model):
    name = models.TextField(max_length=100, null=False)
    parent = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.TextField()
    parent = models.ForeignKey('self', null=True) #self reference

    def __str__(self):
        return self.name


class Feed(models.Model):
    url = models.URLField()
    name = models.TextField(null=True)
    description = models.TextField(null=True)
    last_updated = models.DateTimeField(null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True)

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


class SimilarArticleList(models.Model):
    similar_articles = models.TextField(validators=int_list_validator(
        sep=', ', message=None, code='invalid', allow_negative=False))
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.article_id) + ": " + self.similar_articles


class ArticleTrain(models.Model):
    url = models.URLField(default="")  # default max length=200
    top_image = models.URLField(max_length=2000, null=True)
    title = models.TextField(default="")
    date = models.DateField(null=True)
    text = models.TextField(default="")
    summary = models.TextField(default="")
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return self.title