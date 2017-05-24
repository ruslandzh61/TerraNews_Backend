from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ordinaryPython36.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'uid', 'name', 'email', 'picture')

    def create(self, validated_data):
        return UserProfile.objects.create(**validated_data)


class UserArticleInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserArticleInteraction
        fields = ('id', 'date_accessed', 'user', 'article')


class ArticleSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField('get_article_publisher_name')
    publisher_logo = serializers.SerializerMethodField('get_article_publisher_logo')

    def get_article_publisher_name(self, article):
        return Publisher.objects.get(feed__id=article.feed_id).name

    def get_article_publisher_logo(self, article):
        return Publisher.objects.get(feed__id=article.feed_id).logo

    class Meta:
        model = Article
        fields = ('id', 'url', 'top_image', 'title', 'date', 'text', 'summary', 'feed_id',
                  'publisher_name', 'publisher_logo')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')



class ChannelSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField('get_channel_logo')

    def get_channel_logo(self, channel):
        if ChannelCategory.objects.filter(following_channel=channel).exists():
            channel_category = ChannelCategory.objects.filter(following_channel=channel).last()
            return Article.objects.filter(feed__category=channel_category.category).last().top_image
        if channel.is_system_channel:
            publisher = Publisher.objects.get(id=ChannelPublisher.objects.get(following_channel=channel).publisher_id)
            return publisher.logo
        elif ChannelPublisher.objects.filter(following_channel=channel).exists():
            channel_publisher = ChannelPublisher.objects.filter(following_channel=channel).last()
            return Article.objects.filter(feed__publisher=channel_publisher.publisher).last().top_image
        return None

    class Meta:
        model = Channel
        fields = ('id', 'name', 'user', 'is_system_channel', 'logo')


class ChannelCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField('get_channel_category_name')
    category_image =serializers.SerializerMethodField('get_channel_category_image')

    def get_channel_category_name(self, channel_category):
        return channel_category.category.name

    def get_channel_category_image(self, channel_category):
        return Article.objects.filter(feed__category=channel_category.category).last().top_image

    class Meta:
        model = ChannelCategory
        fields = ('id', 'following_channel', 'category', 'category_name', 'category_image')


class ChannelFeedSerializer(serializers.ModelSerializer):
    feed_name = serializers.SerializerMethodField('get_feed_name')
    feed_url = serializers.SerializerMethodField('get_feed_url')
    feed_picture = serializers.SerializerMethodField('get_feed_url')

    def get_feed_url(self, channel_feed):
        return Feed.objects.get(id=channel_feed.feed).url

    def get_feed_name(self, channel_feed):
        return Feed.objects.get(id=channel_feed.feed).name

    class Meta:
        model = ChannelFeed
        fields = ('id', 'following_channel', 'feed', 'feed_name','feed_url')


class ChannelPublisherSerializer(serializers.ModelSerializer):
    publisher_name = serializers.SerializerMethodField('get_publisher_name')
    publisher_logo = serializers.SerializerMethodField('get_publisher_logo')

    def get_publisher_name(self, channel_publisher):
        return channel_publisher.publisher.name

    def get_publisher_logo(self, channel_publisher):
        return channel_publisher.publisher.logo

    class Meta:
        model = ChannelPublisher
        fields = ('id', 'following_channel', 'publisher', 'publisher_name', 'publisher_logo')

class CollectionSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField('get_collection_logo')

    def get_collection_logo(self, collection):
        return Article.objects.get(id=CollectionArticle.objects.filter(
            collection=collection.id).last().article.id).top_image

    class Meta:
        model = Collection
        fields = ('id', 'name', 'logo')