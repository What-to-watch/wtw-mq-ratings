CREATE TABLE ratings (
    user_id integer,
    movie_id integer,
    rating real,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, movie_id)
)