LOAD CSV WITH HEADERS FROM 'file:///ml_left_join_ym.csv' AS row

MERGE (Item:Item_ML {
  title: row.title,
  movieId: row.movieId
})

MERGE (User:User_ML {
  userId: CASE WHEN row.userId <> '' THEN row.userId ELSE "wow" END
})

MERGE (Release_Date:ReleaseYear_ML {
  year: row.release_year
})

MERGE (Type1:type1_ML {
  genre: CASE WHEN row.genres_ml <> '' THEN row.genres_ml ELSE "wow" END
})


MERGE (Performer1:Performer_YM {
  name: CASE WHEN row.cast <> '' THEN row.cast ELSE "wow" END
})

MERGE (Producer1:Director_YM {
  name: CASE WHEN row.Director <> '' THEN row.Director ELSE "wow" END
})

MERGE (Producer2:Screenwriter_YM {
  name: CASE WHEN row.Screenwriter <> '' THEN row.Screenwriter ELSE "wow" END
})

MERGE (Gender:gender_ML {
  genre: CASE WHEN row.gender <> '' THEN row.gender ELSE "wow" END
})

MERGE (Age:age_ML {
  genre: CASE WHEN row.age <> '' THEN row.age ELSE "wow" END
})

MERGE (Occupation:occupation_ML {
  genre: CASE WHEN row.occupation <> '' THEN row.occupation ELSE "wow" END
})

MERGE (User)-[:RATED_ML {rating: CASE WHEN row.rating <> '' THEN toFloat(row.rating) ELSE "wow" END}]->(Item)
MERGE (Item)-[:TYPE_OF]->(Type1)
MERGE (Item)-[:PRODUCED_BY]->(Producer1)
MERGE (Item)-[:PRODUCED_BY]->(Producer2)
MERGE (Item)-[:RELEASED_IN]->(Release_Date)
MERGE (Item)-[:PERFORMED_BY]->(Performer1)
MERGE (User)-[:GENDER_IS]->(Gender)
MERGE (User)-[:AGE_IS]->(Age)
MERGE (User)-[:WORK_AS]->(Occupation);