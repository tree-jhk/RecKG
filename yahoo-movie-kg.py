import pandas as pd
from utils import *
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default="./data/yahoo_movie_dataset", type=str)
    parser.add_argument("--save_path", default="./data", type=str)
    parser.add_argument("--kg_ratio", default=0.0023, type=float)
    args = parser.parse_args()

    with open(os.path.join(args.data_path, "ydata-ymovies-mapping-to-movielens-v1_0.txt"), 'r', encoding='ISO-8859-1') as file:
        ym_m = file.read()
    ym_m = ym_m.split("\n")

    with open(os.path.join(args.data_path, "ydata-ymovies-movie-content-descr-v1_0.txt"), 'r', encoding='ISO-8859-1') as file:
        ym_meta = file.read()
    ym_meta = ym_meta.split("\n")
    ym_meta = ["\t".join(info.split("\t")[:18]) for info in ym_meta]

    with open(os.path.join(args.data_path, "ydata-ymovies-user-demographics-v1_0.txt"), 'r', encoding='ISO-8859-1') as file:
        ym_u = file.read()
    ym_u = ym_u.split("\n")

    with open(os.path.join(args.data_path, "ydata-ymovies-user-movie-ratings-test-v1_0.txt"), 'r', encoding='ISO-8859-1') as file:
        ym_test = file.read()
    ym_test = ym_test.split("\n")

    with open(os.path.join(args.data_path, "ydata-ymovies-user-movie-ratings-train-v1_0.txt"), 'r', encoding='ISO-8859-1') as file:
        ym_train = file.read()
    ym_train = ym_train.split("\n")

    ym_r = ym_test + ym_train

    ym_m_df, ym_r_df, ym_u_df, ym_meta_df = ym_preprocess_query1(ym_m, ym_r, ym_u, ym_meta)
    ym_kg_neo4j_data = ym_preprocess_query2(ym_m_df, ym_r_df, ym_u_df, ym_meta_df)
    ym_kg_neo4j_data.to_csv(os.path.join(args.save_path, "ym_kg_neo4j_data.csv"), index=False)

    sampled_ml_kg = ml_sample_kg(ym_kg_neo4j_data, args.kg_ratio)
    sampled_ml_kg.to_csv(os.path.join(args.save_path, "sample_ym_kg_neo4j_data.csv"), index=False)