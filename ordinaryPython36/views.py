from django.shortcuts import render
from ordinaryPython36.models import Article, SimilarArticleList, UserProfile
from ordinaryPython36.Supporting.services import SimilarArticleListService, CategoryService, ArticleService, UserProfileService
from ordinaryPython36.Supporting.serializers import ArticleSerializer, CategorySerializer
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class UserProfileList(APIView):
    serializer_class = UserProfile

    def post(self, request, format=None):
        try:
            serializer = UserProfile(data=request.data)
            print(request.data)
            if serializer.is_valid():
                serializer.save()
                return  Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            if "uid" in request.data:
                print("manually add user")
                uid = request.data["uid"]
                print()
                UserProfileService().addUserProfile(uid=uid)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleList(APIView):
    def get(self,request,format=None):
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

class RecommendedArticleList(APIView):
    def get(self, request, format=None):
        if "article" in request.GET:
            article_id = request.GET["article"]
            recommended_articles = SimilarArticleListService().get_similar_articles(article_id)
            serializer = ArticleSerializer(recommended_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return None

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