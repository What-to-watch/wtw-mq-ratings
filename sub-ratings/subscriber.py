from kafka import KafkaConsumer
import json

import psycopg2
from psycopg2 import OperationalError
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


consumer = KafkaConsumer('movie-ratings',
                         group_id='raters',
                         bootstrap_servers=['kafka:9092'],
                         key_deserializer=lambda k: k.decode('utf-8'),
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))
db_connection = create_connection('wtw-poc', 'wtw-poc', 'admin', 'db', '5432')
db_connection.autocommit = True
cursor = db_connection.cursor()

ratings_query = """INSERT INTO ratings (user_id, movie_id, rating) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT (user_id, movie_id) DO UPDATE SET rating = EXCLUDED.rating, timestamp = CURRENT_TIMESTAMP;"""

for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
    cursor.execute(ratings_query, (message.value['user_id'], message.value['movie_id'], message.value['rating']))
    