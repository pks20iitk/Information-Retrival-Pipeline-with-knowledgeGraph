# MATCH (a:Person {name:'Tom Hanks'}) RETURN a
# # Find all the many fine films directed by Steven Spielberg.
# MATCH (director:Person)-[:DIRECTED]->(movie) WHERE director.name = "Steven Spielberg" RETURN movie.title
# # Create a person named Brie Larson Birth 1989
# CREATE (a:Person {name:'Brie Larson', born:1989}) RETURN a
# # Create a movie titled Captain MarvelReleased 2019 Tagline Everything begins with a (her)o.
# CREATE (a:Movie {title:'Captain Marvel', released:2019, tagline:'Everything begins with a (her)o.'}) RETURN a
# # Delete all persons named
# MATCH (a:Person {name:'Brie Larson'}) DETACH DELETE a
# # Delete all movies named Captain Marvel
# MATCH (a:Movie {title:'Captain Marvel'}) DETACH DELETE a
# # Update a person named Brie Larson Birth
# MERGE (a:Person {name:'Brie Larson'}) ON CREATE SET a.born = 1989 ON MATCH SET a.stars = COALESCE(a.stars, 0) + 1 RETURN a
# # Person named Brie Larson acted as Carol Danvers in movie titled
# MATCH (a:Person {name:'Brie Larson'}), (b:Movie {title:'Captain Marvel'})MERGE (a)-[r:ACTED_IN]->(b) SET r.roles = ['Carol Danvers'] RETURN a,r,b
# # Persons with names that start with Tom
# MATCH (a:Person) WHERE a.name STARTS WITH 'Tom' RETURN a
# # Movies released after 1990 but before 2000
# MATCH (a:Movie) WHERE a.released > 1990 AND a.released < 2000 RETURN a
# # List movies with actor Tom Hanks
# MATCH (a:Person {name:'Tom Hanks'})-[:ACTED_IN]->(m:Movie) RETURN a,m
# # Who directed the movie Cloud Atlas
# MATCH (m:Movie {title:'Cloud Atlas'})<-[:DIRECTED]-(d:Person) RETURN d
# # Co-actors of actor Tom Hanks
# MATCH (people:Person)-[relatedTo]-(:Movie {title:'Cloud Atlas'}) RETURN people.name, type(relatedTo), relatedTo
# # How people are related to movie Cloud Atlas
# MATCH (people:Person)-[relatedTo]-(:Movie {title:'Cloud Atlas'}) RETURN people.name, type(relatedTo), relatedTo
# # Movies and actors up to 4 "hops" away from Kevin Bacon
# MATCH (bacon:Person {name:"Kevin Bacon"})-[*1..4]-(hollywood) RETURN DISTINCT hollywood
# # The shortest path following any relationship from Kevin Bacon to Al Pacino
# MATCH p=shortestPath( (bacon:Person {name:"Kevin Bacon"})-[*]-(a:Person {name:'Al Pacino'}) ) RETURN p
# # Extend co-actors, to find co-co-actors who haven't worked with Tom Hanks
# MATCH (a:Person {name:'Tom Hanks'})-[:ACTED_IN]->(m)<-[:ACTED_IN]-(coActors),(coActors)-[:ACTED_IN]->(m2)<-[:ACTED_IN]-(cocoActors)WHERE NOT (a)-[:ACTED_IN]->()<-[:ACTED_IN]-(cocoActors) AND a <> cocoActorsRETURN cocoActors.name AS Recommended, count(*) AS Strength ORDER BY Strength DESC
# # Find someone to introduce Tom Hanks Tom Cruise
# MATCH (a:Person {name:'Tom Hanks'})-[:ACTED_IN]->(m)<-[:ACTED_IN]-(coActors),(coActors)-[:ACTED_IN]->(m2)<-[:ACTED_IN]-(other:Person {name:'Tom Cruise'}) RETURN a, m, coActors, m2, other
