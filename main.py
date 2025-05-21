import random
import json
import uuid
import ast 
import time
from datetime import datetime

from langgraph_sdk import get_client, get_sync_client
from confluent_kafka import Consumer , Producer
from kafka_config import read_config, consumer, producer, postprocess_topic, message_processing_activity_topic

langgraph_client = get_sync_client(url="http://167.99.31.177", api_key="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")

def process_message(body: str):
    """
    Process the message body from Kafka.
    Handles the message as a Python literal instead of strict JSON.
    Args:
        body: The message body as a string        from ai_preprocessing.kafka_config import read_config, consumer, producer, postprocess_topic, message_processing_activity_topic
    """
    print("#################### MESSAGE RECEIVED #################### PROCESSING MESSAGE ####################")
    try:
        data = ast.literal_eval(body)
        producer.produce(message_processing_activity_topic , json.dumps({
            "thread_id": data["thread_id"],
            "org_identifier": data["org_identifier"],
            "type": "preprocessing",
            "created_at": datetime.utcnow().isoformat()
        }))
        producer.flush()
                
        
        producer.produce(message_processing_activity_topic , json.dumps({
            "thread_id": data["thread_id"],
            "org_identifier": data["org_identifier"],
            "type": "ai_processing",
            "created_at": datetime.utcnow().isoformat()
        }))
        producer.flush()
        langgraph_client.threads.create(
            thread_id=data["thread_id"],
            if_exists="do_nothing"
        )
        
        message_ai = langgraph_client.runs.wait(
            thread_id=data["thread_id"],
            input={"messages": [{"type": "human", "content": data["message"]}]},
            assistant_id="agent",
        )
                
        next_step_choices = ["card" , "message" , "button"]
        ai_response = message_ai["messages"][-1]["content"]
        next_step = random.choice(next_step_choices)
        
        producer.produce(postprocess_topic, json.dumps({
            "thread_id": data["thread_id"],
            "message": ai_response,
            "next_step": next_step,
            "org_identifier": data["org_identifier"],
            "page_id": data["page_id"],
            "platform": data["platform"],
            "sender_id": data["sender_id"],
            "created_at": data["created_at"],
            "sender_type": data["sender_type"],
            "destination": "dash",
            "assigned_type": data["assigned_type"]
        }))
        producer.flush()
        
    except Exception as e:
        print(f"Error parsing message body: {e}")
        print(f"Raw message body: {body}")

def consume_kafka():
    print("Starting Kafka consumer...")
    try:
        while True:
            msg = consumer.poll(1.0)  # timeout in seconds
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            # msg.value() is bytes, decode to string
            message = msg.value().decode('utf-8')
            print(f"Received message: {message}")
            process_message(message)
    except KeyboardInterrupt:
        print("Kafka consumer stopped by user.")
    finally:
        consumer.close()

if __name__ == "__main__":
    try:
        consume_kafka()
    except KeyboardInterrupt:
        print("Kafka consumer stopped by user.")
    except Exception as e:
        print(f"Kafka consumer stopped due to error: {e}")
    finally:
        print("Kafka consumer stopped.")
