from django.contrib import admin
from .models import Category, Feed, Article

# Register your models here.
admin.site.register(Category)
admin.site.register(Feed)
admin.site.register(Article)

