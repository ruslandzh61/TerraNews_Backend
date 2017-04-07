from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ordinaryPython36.models import Article, Category, UserProfile, UserArticleInteraction


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
    class Meta:
        model = Article
        fields = ('id', 'url', 'top_image', 'title', 'date', 'text', 'summary', 'feed_id')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')
