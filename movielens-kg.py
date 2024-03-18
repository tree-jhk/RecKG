import pandas as pd
from utils import *
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default="./data/ml-20m/ml-20m", type=str)
    parser.add_argument("--save_path", default="./data", type=str)
    parser.add_argument("--kg_ratio", default=0.0023, type=float)
    args = parser.parse_args()
    
    ml_m = pd.read_csv(os.path.join(args.data_path, "movies.csv"))
    ml_r = pd.read_csv(os.path.join(args.data_path, "ratings.csv"))
    
    ml_kg = pd.merge(ml_r, ml_m, on=["movieId"], how="inner")
    ml_kg, ml_kg_neo4j_data = ml_preprocess_query(ml_kg)
    
    # We sample the subgraph of the KG, since visualization of a full KG is not needed.
    sampled_ml_kg = ml_sample_kg(ml_kg_neo4j_data, args.kg_ratio)
    sampled_ml_kg.to_csv(os.path.join(args.save_path, "ml_kg_neo4j_data.csv"), index=False)