from confluent_kafka import Consumer , Producer


def read_config():
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

kafka_config = read_config()
kafka_config["group.id"] = "preprocessing-group"
consumer = Consumer(kafka_config)
consumer.subscribe(["NewMessagedFromFacebook"])
message_processing_activity_topic = "MessageProcessingActivity"

producer = Producer(kafka_config)
postprocess_topic = "POSTPROCESS"