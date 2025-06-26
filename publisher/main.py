import json
import time
from typing import Dict
from google.cloud import pubsub_v1
from services.extract import extract_data
from services.data import generate_purchase_event
from dotenv import load_dotenv
from utils.config_loader import load_config

load_dotenv()

CONFIG_PATH = "config/config.yaml"
config = load_config(CONFIG_PATH)

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(config['project_id'], config['topic_id'])

def publish_message(data: Dict) -> None:
    """
    Publish a dictionary as a JSON message to a Google Cloud Pub/Sub topic.

    Args:
        data (Dict): The dictionary to be serialized and published.
                     Must be JSON-serializable.
    
    Returns:
        None
    """
    data_str = json.dumps(data)
    data_bytes = data_str.encode("utf-8")
    future = publisher.publish(topic_path, data=data_bytes)
    print(f"Published message ID: {future.result()} - {data_str}")

if __name__ == "__main__":
    """
    Main script execution for publishing simulated purchase messages to Pub/Sub.
    
    It generates dummy customer and product data, simulates purchases, and sends
    10 messages (1 per second) to the configured Pub/Sub topic.
    """
    print("Publishing dummy purchases to Pub/Sub...")
    for _ in range(10):  # publish 10 messages
     
        customer = extract_data("customer")
        product = extract_data("products")
        msg = generate_purchase_event(customer, product)

        publish_message(msg)
        time.sleep(1)  # 1 second interval
