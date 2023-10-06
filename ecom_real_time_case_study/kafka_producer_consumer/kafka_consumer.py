from kafka import KafkaConsumer
from json import loads

from configparser import ConfigParser

KAFKA_CONSUMER_GROUP_NAME_CONS = "test-consumer-group"

# Loading Kafka Cluster/Server details from configuration file(datamaking_app.conf)

conf_file_name = "datamaking_app.conf"
config_obj = ConfigParser()
print(config_obj)
print(config_obj.sections())
config_read_obj = config_obj.read(conf_file_name)
print(type(config_read_obj))
print(config_read_obj)
print(config_obj.sections())

# Kafka Cluster/Server Details
kafka_host_name = config_obj.get('kafka', 'host')
kafka_port_no = config_obj.get('kafka', 'port_no')
kafka_topic_name = config_obj.get('kafka', 'output_topic_name')

KAFKA_TOPIC_NAME_CONS = kafka_topic_name
KAFKA_BOOTSTRAP_SERVERS_CONS = kafka_host_name + ':' + kafka_port_no


if __name__ == "__main__":

    print("Kafka Consumer Application Started ... ")
    try:
        # auto_offset_reset='latest'
        # auto_offset_reset='earliest'
        consumer = KafkaConsumer(
        KAFKA_TOPIC_NAME_CONS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS_CONS,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=KAFKA_CONSUMER_GROUP_NAME_CONS,
        #value_deserializer=lambda x: loads(x.decode('utf-8')))
        value_deserializer=lambda x: x.decode('utf-8'))

        for message in consumer:
            #print(dir(message))
            print(type(message))
            print("Key: ", message.key)
            message = message.value
            print("Message received: ", message)
    except Exception as ex:
        print("Failed to read kafka message.")
        print(ex)