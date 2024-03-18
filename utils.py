import pandas as pd
import requests
import pickle
import random
from typing import List

def tmdb_movie_info(params:dict, movie_id):
    try:
        movie_id = int(movie_id)
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(url, params=params)
        result = dict()
        
        if response.status_code == 200:
            movie_data = response.json()
            result['title'] = movie_data['title']
            result['release_year'] = movie_data['release_date'].split("-")[0]
            result['tmdb_genres'] = '|'.join([info['name'] for info in movie_data['genres']])
            try:
                result['origin_country'] = movie_data['production_companies'][0]['origin_country']
            except:
                result['origin_country'] = 'Null'
        else:
            print(f"movie_id: {movie_id} request fails")
            return None
        
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            credits_data = response.json()
            actors_popularity = {}
            for cast in credits_data['cast']:
                actors_popularity[cast['name']] = cast['popularity']
            
            # Only apply 0 to 2 people with the highest popularity score
            if len(actors_popularity) > 2:
                actors_popularity = sorted(actors_popularity.items(), key=lambda x:(-x[1], x[0]))[:2]
                result['cast'] = '|'.join([name for name, _ in actors_popularity])
            else:
                try:
                    result['cast'] = '|'.join([name for name, _ in actors_popularity.items()])
                except:
                    result['cast'] = ''
                
            job_list = ['Director', 'Original Story', 'Writer', 'Original Film Writer']
            for crew in credits_data['crew']:
                if crew['job'] in job_list:
                    result[crew['job']] = crew['name']
        else:
            print(f"movie_id_credits: {movie_id}_credits request fails")
            return result
        
        return result
    except:
        return None

def get_year(x:str):
    try:
        return str(int(x.split()[-1].strip("\(").strip("\)")) // 10 * 10) + "\'s"
    except:
        return ""

def p_title(x:str):
    try:
        return " ".join(x.split()[:-1])
    except:
        return x

def ml_preprocess_query(ml_kg: pd.DataFrame):
    ml_kg.drop(labels=["timestamp"], axis=1, inplace=True)
    ml_kg = ml_kg[~ml_kg["title"].str.contains(r"1975-1979", regex=True)]
    ml_kg = ml_kg[~ml_kg["title"].str.contains(r"2007-", regex=True)]
    ml_kg[ml_kg["title"].str.contains(r"Frankenstein$", regex=True)]
    ml_kg["release_year"] = ml_kg["title"].apply(lambda x:get_year(x))
    ml_kg["title"] = ml_kg["title"].apply(lambda x:p_title(x))
    ml_kg['genres'] = ml_kg['genres'].str.split("|")
    ml_kg_neo4j_data = ml_kg.explode('genres')
    ml_kg_neo4j_data.sort_values(by=["userId", "movieId", "rating"], ascending=(True, True, False), inplace=True)
    ml_kg_neo4j_data["userId"] = ml_kg_neo4j_data["userId"].apply(lambda x:"ML_" + str(x))
    return ml_kg, ml_kg_neo4j_data

def ml_sample_kg(ml_kg_neo4j_data: pd.DataFrame, ratio: float=0.0023):
    random.seed(1004)
    uid_list = list(ml_kg_neo4j_data.userId.unique())
    sample_uid_list = random.sample(uid_list, round(len(uid_list) * ratio))
    sampled_ml_kg = ml_kg_neo4j_data[ml_kg_neo4j_data['userId'].isin(sample_uid_list)]
    return sampled_ml_kg

def ml_tmdb_preprocess_query(movielens_tmdb_df: pd.DataFrame):
    movielens_tmdb_df = movielens_tmdb_df.drop(labels=["tmdb_genres"], axis=1)
    movielens_tmdb_df["cast"] = movielens_tmdb_df["cast"].apply(lambda x:x.split("|"))
    movielens_tmdb_df = movielens_tmdb_df.explode("cast")
    return movielens_tmdb_df

def ym_preprocess_query1(
                        ym_m: List[str], 
                        ym_r: List[str], 
                        ym_u: List[str], 
                        ym_meta: List[str]
                        ):
    ym_m_dict = {"yahoo_movieId":list(), "title":list(), "movielens_movieId":list()}
    ym_r_dict = {"userId":list(), "yahoo_movieId":list(), "yahoo_style_rating":list(), "rating":list()}
    ym_u_dict = {"userId":list(), "birth_year":list(), "gender":list()}
    ym_meta_dict = {
        "yahoo_movieId":list(), 
        "title":list(), 
        "synopsis":list(), 
        "running_time":list(), 
        "MPAA_rating":list(), 
        "reason_MPAA_rating":list(), 
        "release_date":list(), 
        "release_date1":list(), 
        "distributor":list(), 
        "poster_url":list(), 
        "genres":list(), 
        "directors":list(), 
        "director_ids":list(), 
        "crew":list(), 
        "crew_ids":list(), 
        "crew_types":list(), 
        "actors":list(), 
        "actor_ids":list()
        }

    for val in ym_m:
        try:
            ymid, t, mid = val.split("\t")
            ym_m_dict["yahoo_movieId"].append(ymid)
            ym_m_dict["title"].append(t)
            ym_m_dict["movielens_movieId"].append(mid)
        except:
            print(val)

    for val in ym_r:
        try:
            uid, ymid, yr, r = val.split("\t")
            ym_r_dict["userId"].append(uid)
            ym_r_dict["yahoo_movieId"].append(ymid)
            ym_r_dict["yahoo_style_rating"].append(yr)
            ym_r_dict["rating"].append(r)
        except:
            print(val)

    for val in ym_u:
        try:
            uid, by, gen = val.split("\t")
            ym_u_dict["userId"].append(uid)
            ym_u_dict["birth_year"].append(by)
            ym_u_dict["gender"].append(gen)
        except:
            print(val)

    for val in ym_meta:
        try:
            ymid, t, s, rt, Mr, rMr, rd, rd1, dis, poster, g, d, did, c, cid, ct, a, aid = val.split("\t")
            ym_meta_dict["yahoo_movieId"].append(ymid)
            ym_meta_dict["title"].append(t)
            ym_meta_dict["synopsis"].append(s)
            ym_meta_dict["running_time"].append(rt)
            ym_meta_dict["MPAA_rating"].append(Mr)
            ym_meta_dict["reason_MPAA_rating"].append(rMr)
            ym_meta_dict["release_date"].append(rd)
            ym_meta_dict["release_date1"].append(rd1)
            ym_meta_dict["distributor"].append(dis)
            ym_meta_dict["poster_url"].append(poster)
            ym_meta_dict["genres"].append(g)
            ym_meta_dict["directors"].append(d)
            ym_meta_dict["director_ids"].append(did)
            ym_meta_dict["crew"].append(c)
            ym_meta_dict["crew_ids"].append(cid)
            ym_meta_dict["crew_types"].append(ct)
            ym_meta_dict["actors"].append(a)
            ym_meta_dict["actor_ids"].append(aid)
        except:
            print(val)

    ym_meta_df = pd.DataFrame(ym_meta_dict)
    ym_u_df = pd.DataFrame(ym_u_dict)
    ym_r_df = pd.DataFrame(ym_r_dict)
    ym_m_df = pd.DataFrame(ym_m_dict)

    # Data decontamination on ym_m_df
    # Contamination: Some does not contain yahoo_movieId or some has different title while 'yahoo_movieId' is same.
    contaminated_yahoo_movieId = list(ym_m_df[ym_m_df.yahoo_movieId.duplicated()].yahoo_movieId.unique())
    # print(ym_m_df[ym_m_df.yahoo_movieId.duplicated()]) # -> Check the contaminated data
    ym_m_df = ym_m_df[~ym_m_df.yahoo_movieId.duplicated()]
    # also drop contaminated_yahoo_movieId on ym_meta_df and ym_r_df
    ym_r_df = ym_r_df[~ym_r_df.yahoo_movieId.isin(contaminated_yahoo_movieId)]
    ym_meta_df = ym_meta_df[~ym_meta_df.yahoo_movieId.isin(contaminated_yahoo_movieId)]
    ym_meta_df.drop(labels=["synopsis", "running_time", "MPAA_rating", "release_date", "release_date1", "reason_MPAA_rating", "poster_url", 'director_ids', 'crew_ids', 'actor_ids'], inplace=True, axis=1)
    
    return ym_m_df, ym_r_df, ym_u_df, ym_meta_df

def ym_preprocess_query2(
                        ym_m_df: pd.DataFrame, 
                        ym_r_df: pd.DataFrame, 
                        ym_u_df: pd.DataFrame, 
                        ym_meta_df: pd.DataFrame
                        ):
    ym_kg = pd.merge(ym_r_df, ym_u_df, on=["userId"], how="inner")
    ym_kg.drop_duplicates(inplace=True)
    ym_m_df.drop_duplicates(inplace=True)
    ym_kg = pd.merge(ym_kg, ym_m_df, on=["yahoo_movieId"], how="left")
    ym_kg = pd.merge(ym_kg, ym_meta_df, on=["yahoo_movieId"], how="left")
    def p_genres(x:str):
        if not isinstance(x, str): # for Nan
            return ""
        if "/" in x:
            x = "|".join(x.split("/"))
        return x.split("|")
    ym_kg["genres"] = ym_kg["genres"].apply(lambda x:p_genres(x))
    ym_kg = ym_kg.explode("genres")
    ym_kg_neo4j_data = ym_kg.reset_index()
    ym_kg_neo4j_data.drop(labels=["index"], inplace=True, axis=1)
    ym_kg_neo4j_data.drop(labels=["title_x"], inplace=True, axis=1)
    ym_kg_neo4j_data.rename(columns={"title_y":"title"}, inplace=True)
    ym_kg_neo4j_data = ym_kg_neo4j_data[~ym_kg_neo4j_data.movielens_movieId.isna()]
    for col in ym_kg_neo4j_data.columns:
        ym_kg_neo4j_data[col] = ym_kg_neo4j_data[col].apply(lambda x:x if x != "\\N" else "")
    for col in ym_kg_neo4j_data.columns:
        ym_kg_neo4j_data[col] = ym_kg_neo4j_data[col].fillna("")
    ym_kg_neo4j_data = ym_kg_neo4j_data[~(ym_kg_neo4j_data.birth_year == "0")]
    ym_kg_neo4j_data = ym_kg_neo4j_data[~(ym_kg_neo4j_data.birth_year == "undef")]
    ym_kg_neo4j_data = ym_kg_neo4j_data[(ym_kg_neo4j_data.birth_year.astype(int) >= 1900)]
    ym_kg_neo4j_data["age"] = ym_kg_neo4j_data["birth_year"].apply(lambda x:str((2003 - int(x)) // 10 * 10) + "\'s")
    ym_kg_neo4j_data.drop(labels=["birth_year"], inplace=True, axis=1)
    ym_kg_neo4j_data = ym_kg_neo4j_data[(ym_kg_neo4j_data["title"].str.contains("\(") | ym_kg_neo4j_data["title"].str.contains("\)"))]
    ym_kg_neo4j_data = ym_kg_neo4j_data[(ym_kg_neo4j_data.title.str.contains(" \("))]
    ym_kg_neo4j_data["release_year"] = ym_kg_neo4j_data["title"].apply(lambda x:str(int(x.split()[-1].strip("\(").strip("\)")) // 10 * 10) + "'s")
    ym_kg_neo4j_data["title"] = ym_kg_neo4j_data["title"].apply(lambda x:" ".join(x.split()[:-1]))
    ym_kg_neo4j_data["gender"] = ym_kg_neo4j_data["gender"].apply(lambda x:"M" if x == "m" else "F")
    ym_kg_neo4j_data.drop(labels=["yahoo_movieId", "yahoo_style_rating"], inplace=True, axis=1)
    ym_kg_neo4j_data.rename(columns={"movielens_movieId":"movieId"}, inplace=True)
    ym_kg_neo4j_data["rating"] = ym_kg_neo4j_data["rating"].astype(float)
    ym_kg_neo4j_data.sort_values(by=["userId", "movieId", "rating"], ascending=(True, True, False), inplace=True)
    ym_kg_neo4j_data["userId"] = ym_kg_neo4j_data["userId"].apply(lambda x:"YM_" + str(x))
    return ym_kg_neo4j_data

def ym_sample_kg(ym_kg_neo4j_data: pd.DataFrame, ratio: float=0.013):
    random.seed(1004)
    uid_list = list(ym_kg_neo4j_data.userId.unique())
    sample_uid_list = random.sample(uid_list, round(len(uid_list) * ratio))
    sampled_ml_kg = ym_kg_neo4j_data[ym_kg_neo4j_data['userId'].isin(sample_uid_list)]
    return sampled_ml_kg

def ym_ml_merge(sampled_ml_kg_neo4j_data: pd.DataFrame, ym_kg_neo4j_data: pd.DataFrame):
    def remove_duplicate_rows1(row):
        if row['genres_ml'] == row['genres_ym']:
            return 0
        return 1

    def remove_duplicate_rows2(row):
        return "|".join(row['sorted_genres'])

    ml_left_join_else_data = pd.merge(sampled_ml_kg_neo4j_data, ym_kg_neo4j_data, on=["title", "release_year"], how="left", suffixes=("_ml", "_ym"))
    ml_left_join_else_data = ml_left_join_else_data[["userId_ml", "movieId_ml", "title", "rating_ml", "genres_ml", "genres_ym", "release_year", "distributor"]]
    ml_left_join_else_data = ml_left_join_else_data.rename(columns={"userId_ml":"userId", "movieId_ml":"movieId", "rating_ml":"rating", "genres":"genres_ym"})
    ml_left_join_else_data.drop_duplicates(inplace=True)
    ml_left_join_else_data = ml_left_join_else_data[~ml_left_join_else_data.genres_ym.isna()]
    ml_left_join_else_data.drop_duplicates(inplace=True)

    ml_left_join_else_data['duplicate_flag'] = ml_left_join_else_data.apply(remove_duplicate_rows1, axis=1)
    df_filtered = ml_left_join_else_data[ml_left_join_else_data['duplicate_flag'] == 1]
    df_filtered = df_filtered.drop(columns=['duplicate_flag'])
    df_filtered["sorted_genres"] = df_filtered[['genres_ml', 'genres_ym']].apply(sorted, axis=1)

    df_filtered['unique_genres'] = df_filtered.apply(remove_duplicate_rows2, axis=1)
    df_filtered["sorted_genres"] = df_filtered["sorted_genres"].apply(lambda x:"|".join(x))
    df_filtered = df_filtered.drop_duplicates(subset=['unique_genres', 'userId', 'movieId', 'title', 'rating', 'release_year'])

    df_filtered = df_filtered.drop(columns=['sorted_genres', 'unique_genres'])
    return df_filtered