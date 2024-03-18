LOAD CSV WITH HEADERS FROM 'file:///ml_kg_neo4j_data.csv' AS row

MERGE (Item:Item_ML {
  title: row.title,
  movieId: row.movieId
})

MERGE (User:User_ML {
  userId: CASE WHEN row.userId <> '' THEN row.userId ELSE "wow" END
})

MERGE (Release_Date:ReleaseYear_YM {
  year: row.release_year
})

MERGE (Type1:type1_ML {
  genre: CASE WHEN row.genres_ml <> '' THEN row.genres_ml ELSE "wow" END
})

MERGE (User)-[:RATED_ML {rating: CASE WHEN row.rating <> '' THEN toFloat(row.rating) ELSE "wow" END}]->(Item)
MERGE (Item)-[:TYPE_OF]->(Type1)
MERGE (Item)-[:RELEASED_IN]->(Release_Date);