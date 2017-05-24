from ordinaryPython36.Supporting.services import SimilarArticleListService, CategoryService, ArticleService, \
    UserProfileService, UserArticleInteractionService
from ordinaryPython36.Supporting.serializers import *
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime
from datetime import datetime
from django.utils import timezone
from ordinaryPython36.Supporting.recommendation_engine.recommender import UserCategoryRecommendationEngine
from time import mktime
from datetime import timedelta

# Create your views here.


# if request is personalized work with Channel, ChannelCategory, ChannelFeed, ChannelPublisher tables;
# otherwise with Category, Feed and Publisher

class UserProfileList(APIView):
    #serializer_class = UserProfile

    def post(self, request, format=None):
        if "uid" in request.data:
            print("manually add user")
            uid = request.data["uid"]
            if UserProfile.objects.filter(uid=uid).exists():
                user = UserProfile.objects.get(uid=uid)
                #user.update(**request.data)
                print("user updated")
                if Channel.objects.filter(user=user):
                    for category in CategoryService().get_root_categories():
                        print(category)
                        channel = Channel.objects.create(user=user, is_system_channel=True, name=category.name)
                        ChannelCategory.objects.create(following_channel=channel, category=category)
                return Response(status=status.HTTP_201_CREATED)

            #otherwise:
            try:
                user = UserProfile.objects.create(**request.data)
            except:
                user = UserProfileService().addUserProfile(uid=uid)

            for category in CategoryService().get_root_categories():
                print(category)
                channel = Channel.objects.create(user=user, is_system_channel=True, name=category.name)
                ChannelCategory.objects.create(following_channel=channel, category=category)
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


"""
class ChannelCategoryList(APIView):

    def get(self, request, format=None):
        if 'uid' in request.GET:
            uid = request.data["uid"]
            user_channel_categories = ChannelCategory.objects.filter(following_channel_id__user_id__uid=uid)
            serializer = ChannelCategorySerializer(user_channel_categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    #def delete(self):
"""

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
            UserArticleInteraction.objects.create(**request .data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            if 'user' in request.data and 'article' in request.data:
                user = UserProfile.objects.get(uid=request.data["user"])
                article = Article.objects.get(id=request.data["article"])
                UserArticleInteraction.objects.create(user=user, article=article,
                                                      date_accessed = timezone.now())
                return Response(status=status.HTTP_201_CREATED)
            print("invalid json")
            return Response(status=status.HTTP_400_BAD_REQUEST)

"""
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
        return Response(None, status=status.HTTP_400_BAD_REQUEST)
"""

"""
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
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
"""


class ChannelList(APIView):

    def get(self, request, format=None):
        # if personalized
        if 'uid' in request.GET and 'type' in request.GET:
            uid = request.GET["uid"]
            type = request.GET['type']
            if type == 'system':
                user_channels = Channel.objects.filter(user_id__uid=uid, date_removed__isnull=True,
                                                       is_system_channel=True)
            elif type == 'smart':
                # user created
                user_channels = Channel.objects.filter(user_id__uid=uid, date_removed__isnull=True,
                                                       is_system_channel=False)
            else:
                # all
                user_channels = Channel.objects.filter(user_id__uid=uid, date_removed__isnull=True)
            serializer = ChannelSerializer(user_channels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # default channels - root categories
        default_channels = CategoryService().get_root_categories()
        serializer = CategorySerializer(default_channels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, format=None):
        id = request.data["id"]
        channel = Channel.objects.get(id=id)
        channel.date_removed = timezone.now()
        channel.save()
        print("remove channel")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChannelArticleList(APIView):
    def get(self, request):
        date_from = timezone.now()
        date_from -= timedelta(days=9)
        if 'channel' in request.GET:
            channel_id = request.GET["channel"]
            if Channel.objects.filter(id=channel_id).exists():
                channel = Channel.objects.get(id=channel_id)

            recommended_articles = []

            channel_categories = ChannelCategory.objects.filter(following_channel=channel)
            for channel_category in channel_categories:
                recommended_articles.extend(UserCategoryRecommendationEngine(
                    user_id=channel.user, category_id=channel_category.category,
                datetime_begin=date_from).make_recommendations())

            channel_publishers = ChannelPublisher.objects.filter(following_channel=channel)
            for channel_publisher in channel_publishers:
                feeds = Feed.objects.filter(publisher=channel_publisher.publisher)
                recommended_articles.extend(Article.objects.filter(feed__in=feeds, date__isnull=False).order_by(
                    '-date')[:10])
            serializer = ArticleSerializer(recommended_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif "category" in request.GET:
            category_id = request.GET["category"]
            recommended_articles = UserCategoryRecommendationEngine(
                user_id=None, category_id=category_id, datetime_begin=date_from).__get_top_articles__()
            serializer = ArticleSerializer(recommended_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChannelCategoryList(APIView):
    def get(self, request):
        if 'uid' in request.GET:
            uid = request.GET["uid"]
            if 'channel' in request.GET:
                # categories of specific channel
                channel_id = request.GET['channel']
                channel = Channel.objects.get(id=channel_id)
                channel_categories = ChannelCategory.objects.filter(following_channel=channel)
                serializer = ChannelCategorySerializer(channel_categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # all system categories user is following
                system_channels = Channel.objects.filter(user__uid=uid, is_system_channel=True)
                user_categories = ChannelCategory.objects.filter(following_channel__in=system_channels)
                serializer = ChannelCategorySerializer(user_categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChannelPublisherList(APIView):
    def get(self, request):
        if 'uid' in request.GET:
            uid = request.GET["uid"]
            if 'channel' in request.GET:
                # categories of specific channel
                channel_id = request.GET['channel']
                channel = Channel.objects.get(id=channel_id)
                channel_categories = ChannelPublisher.objects.filter(following_channel=channel)
                serializer = ChannelPublisherSerializer(channel_categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # all system categories user is following
                system_channels = Channel.objects.filter(user__uid=uid, is_system_channel=True)
                user_categories = ChannelPublisher.objects.filter(following_channel__in=system_channels)
                serializer = ChannelPublisherSerializer(user_categories, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChannelCategoryArticleList(APIView):
    def get(self,request,format=None):
        #if personalized
        if "uid" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        elif "category" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_400_BAD_REQUEST)


class ChannelPublisherArticleList(APIView):
    def get(self, request, format=None):
        # if personalized
        if "uid" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        elif "publisher" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_400_BAD_REQUEST)

class ChannelFeedArticleList(APIView):
    def get(self, request, format=None):
        # if personalized
        if "uid" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        elif "feed" in request.GET:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        return Response(None, status=status.HTTP_400_BAD_REQUEST)


"""
# get recommendations for a given category and user
class CategoryRecommendationList(APIView):
    def get(self, request, format=None):
        if "user" in request.GET and "category" in request.GET:
            uid = request.GET["user"]
            user_id = UserProfile.objects.get(uid=uid)
            category_id = request.GET["category"]
            recommended_articles = UserCategoryRecommendationEngine(
                user_id=user_id, category_id=category_id).make_recommendations()
            serializer = ArticleSerializer(recommended_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
"""


# get similar articles
class RelatedArticleList(APIView):
    def get(self, request, format=None):
        if "article" in request.GET:
            article_id = request.GET["article"]
            related_articles = SimilarArticleListService().get_similar_articles(article_id)
            if related_articles is not None:
                related_articles = related_articles.order_by("-date")[:5]
            else:
                return Response(None, status=status.HTTP_200_OK)
            serializer = ArticleSerializer(related_articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

"""
class CategoryList(APIView):
    def get(self, request, format=None):

        if "rootcategory" in request.GET:
            rootCategory = request.GET["rootcategory"]
            categories = CategoryService().getParentWithChildren(rootCategory)
        elif "default" in request.GET:
            categories = CategoryService().get_root_categories()
        else:
            categories = CategoryService().getAll()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
"""

class CollectionList(APIView):
    def get(self, request):
        if 'uid' in request.GET:
            uid = request.GET['uid']
            user = UserProfile.objects.get(uid=uid)
            collections = Collection.objects.filter(user=user)
            serializer = CollectionSerializer(collections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class CollectionDetailsList(APIView):
    def get(self, request):
        if 'collection' in request.GET:
            collection_id = request.GET['collection']
        return Response(status=status.HTTP_400_BAD_REQUEST)
