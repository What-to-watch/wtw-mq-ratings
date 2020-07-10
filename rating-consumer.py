from kafka import KafkaConsumer
import json


consumer = KafkaConsumer('movie-ratings',
                         group_id='raters',
                         bootstrap_servers=['localhost:29092'],
                         key_deserializer=lambda k: k.decode('utf-8'),
                         value_deserializer=lambda v: json.loads(v.decode('utf-8')))

for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))