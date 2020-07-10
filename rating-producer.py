from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for i in range(100):
    key_str = f'{1}-{i}'
    producer.send('movie-ratings', key=key_str, value={'user_id':1, 'movie_id':i, 'rating':3.5})

producer.flush()