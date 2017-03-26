from django.contrib.auth.models import User, Group
from rest_framework import serializers
from ordinaryPython36.models import Article

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class ArticleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Article
		fields = ('url','top_image','title','date','text','summary','feed_id')