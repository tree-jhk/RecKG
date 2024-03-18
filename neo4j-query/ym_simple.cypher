LOAD CSV WITH HEADERS FROM 'file:///sample_ym_kg_neo4j_data.csv' AS row

MERGE (Item:Item_YM {
  title: row.title,
  movieId: row.movieId
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

MERGE (User:User_YM {
  userId: CASE WHEN row.userId <> '' THEN row.userId ELSE "wow" END
})

MERGE (Release_Date:ReleaseYear_YM {
  year: row.release_year
})

MERGE (Type1:type1_YM {
  genre: CASE WHEN row.genres_ym <> '' THEN row.genres_ym ELSE "wow" END
})

MERGE (Gender:gender_YM {
  genre: CASE WHEN row.gender <> '' THEN row.gender ELSE "wow" END
})

MERGE (Age:age_YM {
  genre: CASE WHEN row.age <> '' THEN row.age ELSE "wow" END
})

MERGE (User)-[:RATED_YM {rating: CASE WHEN row.rating <> '' THEN toFloat(row.rating) ELSE "wow" END}]->(Item)
MERGE (User)-[:GENDER_IS]->(Gender)
MERGE (User)-[:AGE_IS]->(Age)
MERGE (Item)-[:TYPE_OF]->(Type1)
MERGE (Item)-[:PRODUCED_BY]->(Producer1)
MERGE (Item)-[:PRODUCED_BY]->(Producer2)
MERGE (Item)-[:RELEASED_IN]->(Release_Date)
MERGE (Item)-[:PERFORMED_BY]->(Performer1);