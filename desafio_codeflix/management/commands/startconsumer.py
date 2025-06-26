import pika
import json
import logging
import time
from django.core.management.base import BaseCommand
from desafio_codeflix.models import Video, AudioVideoMedia, MediaStatus

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start the RabbitMQ consumer for processing video conversion events'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting RabbitMQ consumer...'))
        
        while True:
            try:
                self._consume()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error in consumer: {e}'))
                # Wait a bit before reconnecting
                time.sleep(5)
    
    def _consume(self):
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue='videos.converted', durable=True)
        
        # Define the callback function
        def callback(ch, method, properties, body):
            try:
                # Parse the message
                message = json.loads(body)
                self.stdout.write(self.style.SUCCESS(f'Received message: {message}'))
                
                # Process the message
                self._process_message(message)
                
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing message: {e}'))
                # Reject the message and requeue it
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Set up the consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='videos.converted', on_message_callback=callback)
        
        # Start consuming
        self.stdout.write(self.style.SUCCESS('Waiting for messages. To exit press CTRL+C'))
        channel.start_consuming()
    
    def _process_message(self, message):
        """
        Process a message from the videos.converted queue.
        
        The message should have the following format:
        {
            'video_id': 'uuid',
            'encoded_path': 'path/to/encoded/file'
        }
        """
        video_id = message.get('video_id')
        encoded_path = message.get('encoded_path')
        
        if not video_id or not encoded_path:
            raise ValueError('Invalid message format')
        
        try:
            # Get the video
            video = Video.objects.get(id=video_id)
            
            # Update the media status
            if video.video:
                media = video.video
                media.encoded_path = encoded_path
                media.status = MediaStatus.COMPLETED
                media.save()
                
                self.stdout.write(self.style.SUCCESS(f'Updated media status for video {video_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'Video {video_id} has no associated media'))
        except Video.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Video {video_id} not found'))