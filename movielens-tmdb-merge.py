import pandas as pd
import requests
import pickle
from utils import *
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default="./data/ml-20m/ml-20m", type=str)
    parser.add_argument("--save_path", default="./data", type=str)
    args = parser.parse_args()
    
    # imdb API Key
    api_key = "YOUR IMDB API KEY"
    params = {
        'api_key': api_key,
        'language': 'en-US'  # Can be set to any language
    }
    
    mll = pd.read_csv(os.path.join(args.data_path, "links.csv"))
    mlm = pd.read_csv(os.path.join(args.data_path, "movies.csv"))

    mlid = mll.movieId.unique()
    tmid = mll.tmdbId.unique()

    for i in range(10):
        if not os.path.exists(os.path.join(args.data_path, f"movielens_tmdb_data_{i}.pickle")):
            movielens_tmdb_data = dict()
            
            st = len(mlid) // 10 * (i)
            en = len(mlid) if i == 9 else len(mlid) // 10 * (i + 1)

            for j, (ml_id, tmdb_id) in enumerate(zip(mlid[st:en], tmid[st:en])):
                movielens_tmdb_data[ml_id] = tmdb_movie_info(params, movie_id=tmdb_id)
            
                with open(os.path.join(args.data_path, f"movielens_tmdb_data_{i}.pickle"), 'wb') as fw:
                    pickle.dump(movielens_tmdb_data, fw)
    
    movielens_tmdb_data_dict = dict()
    for i in range(10):
        with open(os.path.join(args.data_path, f"movielens_tmdb_data_{i}.pickle"), "rb") as fr:
            movielens_tmdb_data_dict.update(pickle.load(fr))
    
    attributes = []

    for idx, info in movielens_tmdb_data_dict.items():
        if info is not None:
            for col, val in info.items():
                attributes.append(col)

    attributes = list(set(attributes))
    movielens_tmdb_data = {a:list() for a in ['movieId'] + attributes}

    for mid, info in movielens_tmdb_data_dict.items():
        if info is not None:
            info_keys = list(info.keys())
            movielens_tmdb_data['movieId'].append(mid)
            for col in attributes:
                if col in info_keys:
                    movielens_tmdb_data[col].append(info[col])
                else:
                    movielens_tmdb_data[col].append("")
        else:
            continue

    movielens_tmdb_df = pd.DataFrame(movielens_tmdb_data)
    movielens_tmdb_df = ml_tmdb_preprocess_query(movielens_tmdb_df)
    movielens_tmdb_df.to_csv("./data/movielens_tmdb.csv", index=False)