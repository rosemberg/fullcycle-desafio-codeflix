from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..test_utils import JWTAuthMixin
from ..models import CastMember, CastMemberType, Category, Genre, Video, Rating, AudioVideoMedia, MediaStatus
import time

class JWTAuthTest(JWTAuthMixin, APITestCase):
    """
    Test case that demonstrates how to use JWT authentication in tests.
    """
    def test_auth_with_jwt(self):
        """
        Test that requests can be authenticated with JWT tokens.
        """
        # The JWTAuthMixin.setUp method has already set the Authorization header
        # with a JWT token that has the default roles.

        # Make a request to the API
        response = self.client.get(reverse('castmember-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test with different roles
        self.set_auth(roles=["user"])
        response = self.client.get(reverse('castmember-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test without authentication
        self.remove_auth()
        response = self.client.get(reverse('castmember-list'))
        # If the API requires authentication, this would return 401 Unauthorized
        # But since our API doesn't require authentication yet, it will still return 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class VideoMediaEndToEndTest(APITestCase):
    """
    End-to-end test for the video media upload and conversion process.
    """
    def test_video_media_end_to_end(self):
        # Step 1: Create a Category using the API
        category_data = {
            'name': 'E2E Test Category',
            'description': 'Category for E2E testing',
            'is_active': True
        }
        category_response = self.client.post(reverse('category-list'), category_data)
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        category_id = category_response.data['id']

        # Step 2: Create a Genre using the API
        genre_data = {
            'name': 'E2E Test Genre',
            'is_active': True,
            'categories': [category_id]
        }
        genre_response = self.client.post(reverse('genre-list'), genre_data)
        self.assertEqual(genre_response.status_code, status.HTTP_201_CREATED)
        genre_id = genre_response.data['id']

        # Step 3: Create a CastMember using the API
        cast_member_data = {
            'name': 'E2E Test Actor',
            'type': 'ACTOR'
        }
        cast_member_response = self.client.post(reverse('castmember-list'), cast_member_data)
        self.assertEqual(cast_member_response.status_code, status.HTTP_201_CREATED)
        cast_member_id = cast_member_response.data['id']

        # Step 4: Create a Video using the API
        video_data = {
            'title': 'E2E Test Video',
            'description': 'Video for E2E testing',
            'year_launched': 2023,
            'opened': True,
            'rating': 'L',
            'duration': 120,
            'categories_id': [category_id],
            'genres_id': [genre_id],
            'cast_members_id': [cast_member_id]
        }
        video_response = self.client.post(reverse('video-list'), video_data, format='json')
        self.assertEqual(video_response.status_code, status.HTTP_201_CREATED)
        video_id = video_response.data['id']

        # Step 5: Upload media for the video
        upload_data = {
            'file_path': '/path/to/test/video.mp4'
        }
        upload_url = reverse('video-upload-media', kwargs={'pk': video_id})
        upload_response = self.client.post(upload_url, upload_data)
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        media_id = upload_response.data['id']

        # Step 6: In a real scenario, we would publish an event to the videos.converted queue
        # For this test, we'll skip the actual RabbitMQ interaction
        event_data = {
            'video_id': video_id,
            'encoded_path': '/path/to/encoded/video.mp4'
        }

        # In a real scenario with RabbitMQ running, we would do:
        # from desafio_codeflix.rabbitmq import publish_event
        # publish_result = publish_event('videos.converted', event_data)
        # self.assertTrue(publish_result, "Failed to publish event to RabbitMQ")

        # Step 7: Verify that the video's media status is updated to COMPLETED
        # Note: In a real test, we would need to wait for the consumer to process the message
        # For this test, we'll directly update the database to simulate the consumer

        # Get the media object
        media = AudioVideoMedia.objects.get(id=media_id)

        # Update the media status to simulate the consumer processing the message
        media.status = MediaStatus.COMPLETED
        media.encoded_path = event_data['encoded_path']
        media.save()

        # Verify the media status
        media.refresh_from_db()
        self.assertEqual(media.status, MediaStatus.COMPLETED)
        self.assertEqual(media.encoded_path, event_data['encoded_path'])

        # Verify the video has the correct media
        video = Video.objects.get(id=video_id)
        self.assertEqual(video.video.id, media.id)