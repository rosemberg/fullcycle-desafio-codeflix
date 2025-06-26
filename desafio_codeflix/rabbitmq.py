import pika
import json
import logging

logger = logging.getLogger(__name__)

def publish_event(queue_name, message):
    """
    Publish an event to a RabbitMQ queue.
    
    Args:
        queue_name (str): The name of the queue to publish to.
        message (dict): The message to publish.
    
    Returns:
        bool: True if the message was published successfully, False otherwise.
    """
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Publish the message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        
        # Close the connection
        connection.close()
        
        logger.info(f"Published message to {queue_name}: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish message to {queue_name}: {e}")
        return False