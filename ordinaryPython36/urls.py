
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from ordinaryPython36.views import ArticleList


urlpatterns = [
    url(r'^api/v1/$', ArticleList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
