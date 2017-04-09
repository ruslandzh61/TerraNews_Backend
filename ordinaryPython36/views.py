from django.shortcuts import render
from ordinaryPython36.models import Article, SimilarArticleList, UserProfile, UserArticleInteraction
from ordinaryPython36.Supporting.services import SimilarArticleListService, CategoryService, ArticleService, \
    UserProfileService, UserArticleInteractionService
from ordinaryPython36.Supporting.serializers import ArticleSerializer, CategorySerializer, UserProfileSerializer, \
    UserArticleInteractionSerializer
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime
from datetime import datetime
from django.utils import timezone

from time import mktime

# Create your views here.


class UserProfileList(APIView):
    serializer_class = UserProfile

    def post(self, request, format=None):
        if "uid" in request.data:
            print("manually add user")
            uid = request.data["uid"]
            user = UserProfile.objects.filter(uid=uid)
            if user is not None:
                user.update(**request.data)
                print("user updated")
                return Response(status=status.HTTP_201_CREATED)

        try:
            UserProfile.objects.create(**request.data)
            print("user created")
            return Response(status=status.HTTP_201_CREATED)
        except:
            UserProfileService().addUserProfile(uid=uid)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserArticleInteractionList(APIView):
    serializer_class = UserArticleInteraction

    def post(self, request, format=None):
        # serializer = UserArticleInteraction(data=request.data)
        # if serializer.is_valid():
        #     print("user accessed article")
        #     serializer.save()
        #     return  Response(serializer.data, status=status.HTTP_201_CREATED)
        print(request.data)
        try:
            UserArticleInteraction.objects.create(**request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            if 'user' in request.data and 'article' in request.data:
                user = UserProfile.objects.get(uid=request.data["user"])
                article = Article.objects.get(id=request.data["article"])
                UserArticleInteraction.objects.create(user=user, article=article,
                                                      date_accessed = timezone.now())
                return Response(status=status.HTTP_201_CREATED)
            else:
                print("invalid json")
                return Response(status=status.HTTP_400_BAD_REQUEST)


class ArticleList(APIView):
    def get(self, request, format=None):
        if "feed" in request.GET:
            feed = request.GET["feed"]
            if  "size" in request.GET:
                feed = feed.replace(" ", "+")
                size = request.GET["size"]
            else:
                articles = Article.objects.filter(feed_id__exact=feed).order_by("-date")[:10]
                serializer = ArticleSerializer(articles, many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)

            articles = Article.objects.filter(feed_id__exact=int(feed)).order_by("-date")[:int(size)]
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif "recommend" in request.GET:
            return None
        return None


class ArticleListByCategory(APIView):
    def get(self,request,format=None):
        if "category" in request.GET:
            category = request.GET["category"]
            if "size" in request.GET:
                category = category.replace(" ", "+")
                size = request.GET["size"]
                articles = ArticleService().get_articles_by_category_id_including_children(
                    category).exclude(date__isnull=True).order_by("-date")[:int(size)]
            else:
                articles = ArticleService().get_articles_by_category_id_including_children(
                    root_category_id=category).exclude(date__isnull=True).order_by("-date")[:10]

            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return None

# get recommendations for a given category and user
class CategoryRecommendationList(APIView):
    def get(self, request, format=None):
        if "user" in request.GET and "category" in request.GET:
            user_id = request.GET["user"]
            category_id = request.GET["category"]

# get similar articles
class RelatedArticleList(APIView):
    def get(self, request, format=None):
        if "article" in request.GET:
            article_id = request.GET["article"]
            recommended_articles = SimilarArticleListService().get_similar_articles(article_id).order_by("-date")[:5]
            serializer = ArticleSerializer(recommended_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return None


class CategoryList(APIView):
    def get(self, request, format=None):
        if "rootCategory" in request.GET:
            rootCategory = request.GET["category"]
            categories = CategoryService().getParentWithChildren(rootCategory)
        elif "default" in request.GET:
            categories = CategoryService().get_root_categories()
        else:
            categories = CategoryService().getAll()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)