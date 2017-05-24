
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ordinaryPython36.views import *


urlpatterns = [
    #url(r'^api/v1/feed$', ArticleList.as_view()),
    url(r'^api/v1/relatedarticles$', RelatedArticleList.as_view()),
    #url(r'^api/v1/categories$', CategoryList.as_view()),
    #url(r'^api/v1/categoryarticles$', ArticleListByCategory.as_view()),
    url(r'^api/v1/users$', UserProfileList.as_view()),
    url(r'^api/v1/userarticleinteraction$', UserArticleInteractionList.as_view()),
    url(r'^api/v1/categoryrecommendation$', ChannelArticleList.as_view()),
    url(r'^api/v1/channels$', ChannelList.as_view()),
    url(r'^api/v1/followingcategories$', ChannelCategoryList.as_view()),
    url(r'^api/v1/followingpublishers$', ChannelPublisherList.as_view()),
    url(r'^api/v1/collections$', CollectionList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
