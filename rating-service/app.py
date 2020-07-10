from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

from flask import Flask, request
app = Flask(__name__)

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/rate')
def rate():
    req = request.get_json()
    user_id = int(req['user_id'])
    movie_id = int(req['movie_id'])
    rating = float(req['rating'])

    key_str = f'{user_id}-{movie_id}'
    future = producer.send('movie-ratings', key=key_str, value={'user_id':user_id, 'movie_id':movie_id, 'rating':rating})
    try:
        record_metadata = future.get(timeout=10)
        return {
            "status":"Success"
        }
    except KafkaError:
         return {
            "status":"Failed"
        }