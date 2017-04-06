from ordinaryPython36.Supporting.services import ArticleService, SimilarArticleListService
from sklearn.feature_extraction.text import TfidfVectorizer
from ordinaryPython36.models import Article, SimilarArticleList
from sklearn.metrics.pairwise import linear_kernel
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import roc_auc_score
import random
import numpy as np
import scipy.sparse as sp


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


class KNN:
    def create_training_sets(self, ratings, n_training, n_testing):
        print ("Creating user movie-interaction lists")
        #print(len(list(ratings)))
        user_interactions_dict = defaultdict(set)
        max_movie_id = 0
        #dictionary: map user_id
        for r in ratings:
            user_interactions_dict[r.user_id].add(r.movie_id)
            max_movie_id = max(max_movie_id, r.movie_id)

        user_interactions = list(user_interactions_dict.values()) #user_int is now list of set of interactions
        #get random sampling from data for training and testing
        sampled_indices = random.sample(range(len(user_interactions)), n_training + n_testing)

        #separate on training and testing
        users = []
        movies = []
        interactions = []
        for new_user_id, idx in enumerate(sampled_indices[:n_training]):
            users.extend([new_user_id] * len(user_interactions[idx]))
            movies.extend(user_interactions[idx])
            interactions.extend([1.] * len(user_interactions[idx])) #rate all interactions as 1
        #users[idx], movies[idx], interaction[idx] - all correspond to the same user
        n_movies = max_movie_id + 1
        training_matrix = sp.coo_matrix((interactions, (users, movies)),
                                        shape=(n_training, n_movies)).tocsr()

        users = []
        movies = []
        interactions = []
        for new_user_id, idx in enumerate(sampled_indices[n_training:]):
            """
            print(new_user_id, idx)
            print("ratings: ", ratings[idx].user_id)
            for user_id_t, interactions_t in user_interactions_dict.items():
                if interactions_t == user_interactions[idx]:
                    print("user_id: ", user_id_t, interactions_t)
            """

            users.extend([new_user_id] * len(user_interactions[idx]))
            movies.extend(user_interactions[idx])
            interactions.extend([1.] * len(user_interactions[idx]))

        n_movies = max_movie_id + 1
        testing_matrix = sp.coo_matrix((interactions, (users, movies)),
                                       shape=(n_testing, n_movies)).tocsr()

        print(training_matrix.shape, testing_matrix.shape)

        return training_matrix, testing_matrix

    def train_and_score(self, training, testing, metric="cosine", ks=[10]):
        print("Training and scoring")
        knn = NearestNeighbors(metric=metric, algorithm="brute")
        knn.fit(training)
        for k in ks:
            print("Evaluating for", k, "neighbors")

            neighbor_indices = knn.kneighbors(testing,
                                              n_neighbors=k,
                                              return_distance=False) #get K nearest neighbors' indices (k indices)
            #print("distance: ", distance)
            all_predicted_scores = []
            all_labels = [] #actual interactions
            for user_id in range(testing.shape[0]): #row (n_testing)
                user_row = testing[user_id, :] #format row, col, value
                _, interaction_indices = user_row.nonzero() #get only indices of movies user interracted with
                # number of movies the given user have interracted
                interacted = set(interaction_indices)
                # number of movies the given user have not interracted
                non_interacted = set(range(testing.shape[1])) - interacted #shape[1] - all movies;

                # randomly chosse an equal number of movies user had and had not interacted with.
                # Thus, each positive training or test example had a corresponding negative example (no class imbalance).
                n_samples = min(len(non_interacted), len(interacted))
                sampled_interacted = random.sample(interacted, n_samples)
                sampled_non_interacted = random.sample(non_interacted, n_samples)

                indices = list(sampled_interacted)
                indices.extend(sampled_non_interacted)
                #true labels of the user
                labels = [1] * n_samples # fill in with interructed
                labels.extend([0] * n_samples) # fill in with non-interructed

                # For each vector in the query set, the k closest reference vectors are returned
                # average the interaction vectors of the k neighbors to get an interaction score between 0 and 1 for each movie.
                print("neighbor_indices: ", neighbor_indices[user_id, :])
                print("training_neighbor_indices", training[neighbor_indices[user_id, :], :])
                # get indices of the closest neighbors of the user, then get all the interactions of knn
                neighbors = training[neighbor_indices[user_id, :], :] # first - neighbor id from 0 to k-1, second - movie ids
                predicted_scores = neighbors.mean(axis=0)

                #for i in predicted_scores[0, 0]:
                    # print(i)
                for idx in indices:
                    all_predicted_scores.append(predicted_scores[0, idx]) #predicted interructions for the given user
                all_labels.extend(labels) # actual interructions of the given user with id - user_id

            print(len(all_labels), len(all_predicted_scores))
            print(all_labels)
            print(all_predicted_scores)
            auc = roc_auc_score(all_labels, all_predicted_scores) #evaluate whether users are similar

            print("k", k, "AUC", auc)

    def get_data(self, ratings, n_training, n_testing): # n_training and n_testing - number of users
        # actual user_id is user_id+1, movie_id is movie_id+1
        print ("Creating user movie-interaction lists")
        #print(len(list(ratings)))
        user_interactions_dict = defaultdict(set)
        max_movie_id = 0
        #dictionary: map actual user_id
        for r in ratings:
            user_interactions_dict[r.user_id].add(r.movie_id)
            max_movie_id = max(max_movie_id, r.movie_id)
        user_ids = user_interactions_dict.keys()
        #print("keys: ", user_ids)
        #get random sampling from data for training and testing
        sampled_indices = list(user_ids)[10:n_training+n_testing+10] #random.sample(range(len(user_ids)), n_training + n_testing)
        #print("sampled indices: ", sampled_indices)
        #separate on training and testing
        users = []
        movies = []
        interactions = []
        new_old_user_id_training_dict = dict()
        for new_user_id, old_user_id in enumerate(sampled_indices[:n_training]):
            new_old_user_id_training_dict[new_user_id] = old_user_id
            users.extend([new_user_id] * 10)  # array consisting of n user_id (n is number of rated movies)
            interactions.extend([1.] * 10)  # rate 10 interactions as 1
            list_from_set = list(user_interactions_dict[old_user_id])
            for i in range(10):
                movies.extend([list_from_set[i]]) #add first 10 rated movies

        #users[idx], movies[idx], interaction[idx] - all correspond to the same user
        print(len(users), len(movies), len(interactions))
        n_movies = max_movie_id + 1
        training_matrix = sp.coo_matrix((interactions, (users, movies)),
                                        shape=(n_training, n_movies)).tocsr()

        users = []
        movies = []
        interactions = []
        new_old_user_id_testing_dict = dict()
        for new_user_id, old_user_id in enumerate(sampled_indices[n_training:]):
            new_old_user_id_testing_dict[new_user_id] = old_user_id
            users.extend([new_user_id] * 10)  # array consisting of n user_id (n is number of rated movies)
            interactions.extend([1.] * 10)  # rate 10 interactions as 1
            list_from_set = list(user_interactions_dict[old_user_id])
            for i in range(10):
                movies.extend([list_from_set[i]])  # add first 10 rated movies

        # users[idx], movies[idx], interaction[idx] - all correspond to the same user
        print(len(users), len(movies), len(interactions))
        n_movies = max_movie_id + 1

        testing_matrix = sp.coo_matrix((interactions, (users, movies)), shape=(n_testing, n_movies)).tocsr()

        print(training_matrix.shape, testing_matrix.shape)

        return training_matrix, testing_matrix, new_old_user_id_training_dict, new_old_user_id_testing_dict

    def predict(self, training, testing, metric="cosine", k=5):
        # actual user_id is user_id+1, movie_id is movie_id+1
        print("Training and scoring")
        knn = NearestNeighbors(metric=metric, algorithm="brute")
        knn.fit(training)

        # get K nearest neighbors' indices (k indices)
        similarities, neighbor_indices = knn.kneighbors(testing, n_neighbors=k, return_distance=True)
        # map user_id to a list of tuples (movie_id, number of KNNs, who rated it)
        user_recommended_movies_dict = defaultdict(list)

        for user_id in range(testing.shape[0]): #row (n_testing)
            # For each vector in the query set, the k closest reference vectors are returned
            # average the interaction vectors of the k neighbors to
            # get an interaction score between 0 and 1 for each movie.
            # neighbors = training[neighbor_indices[user_id, :], :] get indices of the closest neighbors of the user
            # print(neighbors)
            similarities_dict = dict()  # map neighbor_id to similarity rate
            print(similarities[user_id])
            print(neighbor_indices[user_id])  # users_train_dict
            for idx, similarity in enumerate(similarities[user_id]):
                similarities_dict[neighbor_indices[user_id, idx]] = similarity
            movie_id_score_dict = defaultdict(list)
            start = 0
            for neighbor, end in enumerate(training.indptr[1:]):
                if neighbor not in neighbor_indices[user_id]:  # not closest neighbor
                    start = end
                    continue
                for movie_id, rating in zip(training.indices[start:end], training.data[start:end]):
                    print(neighbor, ": ", movie_id, rating)
                    rating *= similarities_dict[neighbor]
                    # print(neighbor, users_train_dict[neighbor], ": ", movie_id, rating)
                    movie_id_score_dict[movie_id].append(rating)
                start = end
            print("movie dict:")
            for movie_id, rating in movie_id_score_dict.items():
                print(movie_id, ": ", len(rating), ": ", 1.0)
                # since rating is binary and only rated items are considered, predicted score is always 1.0
                # in case if the rating is not binary or matrix is not sparse then find mean
                user_recommended_movies_dict[user_id].append((movie_id, len(rating)))
                # users_train_dict[user_id]
        # for i in user_recommended_movies_dict.keys():
        #     print(i, ": ", user_recommended_movies_dict[i])
        return user_recommended_movies_dict