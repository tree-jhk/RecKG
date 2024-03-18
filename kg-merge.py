import pandas as pd
from utils import *
import argparse
import os
import copy


if __name__ == '__main__':
    sampled_ml_kg_neo4j_data = pd.read_csv("./data/ml_kg_neo4j_data.csv")
    ym_kg_neo4j_data = pd.read_csv("./data/ym_kg_neo4j_data.csv")

    merged_data = ym_ml_merge(sampled_ml_kg_neo4j_data, ym_kg_neo4j_data)
    merged_data.to_csv("./data/ml_left_join_ym.csv", index=False)