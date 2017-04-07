import feedparser
from ordinaryPython36.Supporting.services import FeedService
from ordinaryPython36.Supporting.text_summarizer import FrequencySummarizer
from ordinaryPython36.models import Feed, Article
from newspaper import Article as newspaperArticle
from time import mktime
from datetime import datetime
import urllib.error
from django.utils import timezone


class Aggregator:
    frequencySummarizer = FrequencySummarizer()
    def aggregate(self, category_id):
        print("Aggregate category: %d", category_id)
        print("-----------------------------------")
        fds = FeedService()
        feedmodels = fds.get_feeds_by_category_id(category_id)
        for feedmodel in feedmodels:
            try:
                print("aggregate: " + feedmodel.url)
                feed = feedparser.parse(feedmodel.url)

                if 'feed' in feed and 'updated_parsed' in feed.feed:
                    updated_parsed = datetime.fromtimestamp(mktime(feed.feed['updated_parsed']))
                    if feedmodel.last_updated == updated_parsed:
                        print("Feed has not been updated yet")
                        continue

                    feedmodel.last_updated = updated_parsed
                    feedmodel.save()

                for article in feed.entries:
                    #item
                    # check if it is already contained in the database in the same feed
                    if Article.objects.filter(url=article.link, feed=feedmodel).count() > 0:
                        print("Article already exists in the same feed")
                        continue #'break' if there is the same link from this feed, problem: articles in feed may non be ordered according to the date

                    #check if it is already contained in the database in any other feed
                    if Article.objects.filter(url=article.link).count() > 0:
                        print("Article ", article.link, " (feed:", feedmodel.id, ") " "already exists in another feed")
                        continue

                    # preprocessing article
                    parser = newspaperArticle(article.link)
                    parser.download()
                    if parser.is_downloaded:
                        parser.parse()
                    else:
                        print("newspaper failed to download article: ", article.link)

                    publish_date = None
                    if 'published_parsed' in article:
                        try:
                            publish_date = datetime.fromtimestamp(mktime(article.published_parsed))
                        except TypeError:
                            print("publish_date is not of type tuple or struct_time")
                            if publish_date is not None:
                                publish_date = datetime(article.published_parsed)
                            else:
                                publish_date = parser.publish_date
                                #if publish_date is None:
                                    #publish_date = timezone.now()

                    title = article.title
                    if title is None:
                        title = parser.title

                    summary = None
                    if 'summary' in article:
                        summary = article.summary
                        if summary is None or ( summary is not None and summary == ''):
                            summary = Aggregator.frequencySummarizer.summarize(parser.text.replace("\n", " "), 5)
                            print("Summerize: " + article.link)

                    # add to database
                    Article.objects.create(
                        url=article.link, title=title,
                        text=parser.text, date=publish_date,
                        summary=summary,
                        top_image=parser.top_image, feed=feedmodel)

                    # Tagging
                    # parser.nlp()
                    # print(article.keywords)

                    # sentiment analysis
                    #t = TextBlob(article.text)
                    #print(t.sentiment.polarity)
            except urllib.error.URLError:
                print("Invalid URL specified: " + feedmodel.url)
                continue

    def update_publisher_logo(self):
        f = Feed.objects.all().distinct('publisher')
        for fi in f:
            p = fi.publisher
            print(p.name)
            feed = feedparser.parse(fi.url)
            if 'feed' in feed and 'image' in feed.feed and 'link' in feed.feed.image:
                p.logo = feed.feed.image.link
                p.save()