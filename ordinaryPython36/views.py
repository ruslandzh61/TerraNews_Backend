from django.shortcuts import render
from ordinaryPython36.models import Article
from ordinaryPython36.Supporting.serializers import ArticleSerializer
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class ArticleList(APIView):
    def get(self,request,format=None):
        if "feed" in request.GET and "size" in request.GET:
            feed = request.GET["feed"]
            feed = feed.replace(" ", "+")
            size = request.GET["size"]
        else:
            articles = Article.objects.filter(feed_id__exact=10).order_by("-date")[:5]
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)

        articles = Article.objects.filter(feed_id__exact=int(feed)).order_by("-date")[:int(size)]
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
