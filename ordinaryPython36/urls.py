
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ordinaryPython36.views import ArticleList, RecommendedArticleList, CategoryList, ArticleListByCategory, \
    UserProfileList, UserArticleInteractionList


urlpatterns = [
    url(r'^api/v1/feed$', ArticleList.as_view()),
    url(r'^api/v1/recommendedlist$', RecommendedArticleList.as_view()),
    url(r'^api/v1/categories$', CategoryList.as_view()),
    url(r'^api/v1/categoryarticles$', ArticleListByCategory.as_view()),
    url(r'^api/v1/users$', UserProfileList.as_view()),
    url(r'^api/v1/userarticleinteraction$', UserArticleInteractionList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
