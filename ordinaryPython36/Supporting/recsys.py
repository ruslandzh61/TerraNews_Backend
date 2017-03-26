from ordinaryPython36.Supporting.services import ArticleService, SimilarArticleListService
from sklearn.feature_extraction.text import TfidfVectorizer
from ordinaryPython36.models import Article, SimilarArticleList
from sklearn.metrics.pairwise import linear_kernel


class ContentEngine:
    def train(self, category_id):
        article_list_of_dicts = ArticleService().get_articles_by_category_id_including_children(
            category_id).values('id', 'text').order_by('id')
        if article_list_of_dicts.count() < 1:
            return

        artcle_ids = article_list_of_dicts.values_list('id', flat=True)
        artcle_texts = article_list_of_dicts.values_list('text', flat=True)
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')

        tfidf_matrix = tf.fit_transform(artcle_texts)

        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

        for idx in range(0, article_list_of_dicts.count()):  # article_dic instead idx and row
            # article_ids[idx] - current article id

            """x = numpy.array([1.48,1.41,0.0,0.1])
                        print x.argsort()
                        [2 3 1 0]"""
            similar_indices = cosine_similarities[idx].argsort()[:-12:-1]  # get indices of 10 most similar items
            similar_articles = []
            for i in similar_indices:
                if cosine_similarities[idx][i] < 0.05:
                    break
                if i == idx:
                    continue

                similar_articles.append(str(artcle_ids[int(i)]))

            similiarity_list_model = SimilarArticleListService().get_similiarity_list(article_id=artcle_ids[idx])
            if similiarity_list_model != None:
                old = similiarity_list_model.similar_articles.split(', ')
                resulting = old + list(set(set(similar_articles)) - set(old))
                similiarity_list_model.similar_articles = ', '.join(resulting)
                similiarity_list_model.save()
            else:
                SimilarArticleList.objects.create(similar_articles=', '.join(similar_articles),
                                                  article=Article.objects.get(id=artcle_ids[idx]))

    def predict(self, article):
        return SimilarArticleListService().get_similar_articles(article)