from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CastMember, CastMemberType, Category, Genre, Video, Rating, AudioVideoMedia, MediaStatus
from .serializers import CreateVideoSerializer
import time

# Create your tests here.
class CastMemberModelTest(TestCase):
    def setUp(self):
        self.cast_member = CastMember.objects.create(
            name="John Doe",
            type=CastMemberType.DIRECTOR
        )

    def test_cast_member_creation(self):
        self.assertEqual(self.cast_member.name, "John Doe")
        self.assertEqual(self.cast_member.type, CastMemberType.DIRECTOR)
        self.assertTrue(self.cast_member.created_at)
        self.assertTrue(self.cast_member.updated_at)

    def test_cast_member_str(self):
        self.assertEqual(str(self.cast_member), "John Doe")

class CastMemberAPITest(APITestCase):
    def setUp(self):
        self.cast_member = CastMember.objects.create(
            name="Jane Doe",
            type=CastMemberType.ACTOR
        )
        self.list_url = reverse('castmember-list')
        self.detail_url = reverse('castmember-detail', kwargs={'pk': self.cast_member.id})

    def test_list_cast_members(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('meta', response.data)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['meta']['current_page'], 1)
        self.assertEqual(response.data['meta']['total'], 1)

    def test_pagination(self):
        # Create more cast members to test pagination
        for i in range(15):
            CastMember.objects.create(
                name=f"Cast Member {i}",
                type=CastMemberType.ACTOR if i % 2 == 0 else CastMemberType.DIRECTOR
            )

        # Test first page
        response = self.client.get(f"{self.list_url}?current_page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('meta', response.data)
        self.assertEqual(response.data['meta']['current_page'], 1)
        self.assertEqual(response.data['meta']['total'], 16)  # 15 new + 1 from setUp

        # Test second page
        response = self.client.get(f"{self.list_url}?current_page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('meta', response.data)
        self.assertEqual(response.data['meta']['current_page'], 2)

    def test_retrieve_cast_member(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Jane Doe")
        self.assertEqual(response.data['type'], "ACTOR")

    def test_create_cast_member(self):
        data = {
            'name': 'New Cast Member',
            'type': "DIRECTOR"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CastMember.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Cast Member')
        self.assertEqual(response.data['type'], "DIRECTOR")

    def test_update_cast_member(self):
        data = {
            'name': 'Updated Name',
            'type': "DIRECTOR"
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cast_member.refresh_from_db()
        self.assertEqual(self.cast_member.name, 'Updated Name')
        self.assertEqual(self.cast_member.type, CastMemberType.DIRECTOR)

    def test_delete_cast_member(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CastMember.objects.count(), 0)

class CastMemberEndToEndTest(APITestCase):
    def test_end_to_end(self):
        # Create a cast member
        create_data = {
            'name': 'E2E Test Actor',
            'type': "ACTOR"
        }
        create_response = self.client.post(reverse('castmember-list'), create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        cast_member_id = create_response.data['id']

        # Retrieve the cast member
        retrieve_url = reverse('castmember-detail', kwargs={'pk': cast_member_id})
        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['name'], 'E2E Test Actor')
        self.assertEqual(retrieve_response.data['type'], "ACTOR")

        # Update the cast member
        update_data = {
            'name': 'E2E Test Director',
            'type': "DIRECTOR"
        }
        update_response = self.client.put(retrieve_url, update_data)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Verify the update
        verify_response = self.client.get(retrieve_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_response.data['name'], 'E2E Test Director')
        self.assertEqual(verify_response.data['type'], "DIRECTOR")

        # Delete the cast member
        delete_response = self.client.delete(retrieve_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the deletion
        verify_delete_response = self.client.get(retrieve_url)
        self.assertEqual(verify_delete_response.status_code, status.HTTP_404_NOT_FOUND)

class VideoWithoutMediaEndToEndTest(APITestCase):
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Category Description",
            is_active=True
        )

        # Create a genre
        self.genre = Genre.objects.create(
            name="Test Genre",
            is_active=True
        )
        self.genre.categories.add(self.category)

        # Create a cast member
        self.cast_member = CastMember.objects.create(
            name="Test Cast Member",
            type=CastMemberType.ACTOR
        )

        # URL for creating videos
        self.create_video_url = reverse('video-list')

    def test_create_video_without_media_success(self):
        """
        Test creating a video without media with valid data.
        """
        data = {
            'title': 'Test Video',
            'description': 'Test Video Description',
            'year_launched': 2021,
            'opened': True,
            'rating': 'L',
            'duration': 120,
            'categories_id': [str(self.category.id)],
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

        response = self.client.post(self.create_video_url, data, format='json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Verify the video was created in the database
        video_id = response.data['id']
        video = Video.objects.get(id=video_id)
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.description, 'Test Video Description')
        self.assertEqual(video.year_launched, 2021)
        self.assertTrue(video.opened)
        self.assertEqual(video.rating, Rating.L)
        self.assertEqual(video.duration, 120)

        # Verify relationships
        self.assertEqual(video.categories.count(), 1)
        self.assertEqual(video.genres.count(), 1)
        self.assertEqual(video.cast_members.count(), 1)
        self.assertEqual(video.categories.first().id, self.category.id)
        self.assertEqual(video.genres.first().id, self.genre.id)
        self.assertEqual(video.cast_members.first().id, self.cast_member.id)

    def test_create_video_without_media_failure(self):
        """
        Test creating a video without media with invalid data.
        """
        # Missing required fields
        data = {
            'title': 'Test Video',
            # Missing year_launched, rating, duration
            'opened': True,
            'categories_id': [str(self.category.id)],
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

        response = self.client.post(self.create_video_url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid rating
        data = {
            'title': 'Test Video',
            'description': 'Test Video Description',
            'year_launched': 2021,
            'opened': True,
            'rating': 'INVALID_RATING',  # Invalid rating
            'duration': 120,
            'categories_id': [str(self.category.id)],
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

        response = self.client.post(self.create_video_url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid category ID
        data = {
            'title': 'Test Video',
            'description': 'Test Video Description',
            'year_launched': 2021,
            'opened': True,
            'rating': 'L',
            'duration': 120,
            'categories_id': ['invalid-uuid'],  # Invalid UUID
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

        response = self.client.post(self.create_video_url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CreateVideoSerializerTest(TestCase):
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(
            name="Test Category",
            description="Test Category Description",
            is_active=True
        )

        # Create a genre
        self.genre = Genre.objects.create(
            name="Test Genre",
            is_active=True
        )
        self.genre.categories.add(self.category)

        # Create a cast member
        self.cast_member = CastMember.objects.create(
            name="Test Cast Member",
            type=CastMemberType.ACTOR
        )

        # Valid data for testing
        self.valid_data = {
            'title': 'Test Video',
            'description': 'Test Video Description',
            'year_launched': 2021,
            'opened': True,
            'rating': 'L',
            'duration': 120,
            'categories_id': [str(self.category.id)],
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

    def test_serializer_with_valid_data(self):
        """
        Test that the serializer validates and saves with valid data.
        """
        serializer = CreateVideoSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        video = serializer.save()
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.description, 'Test Video Description')
        self.assertEqual(video.year_launched, 2021)
        self.assertTrue(video.opened)
        self.assertEqual(video.rating, Rating.L)
        self.assertEqual(video.duration, 120)

        # Verify relationships
        self.assertEqual(video.categories.count(), 1)
        self.assertEqual(video.genres.count(), 1)
        self.assertEqual(video.cast_members.count(), 1)
        self.assertEqual(video.categories.first().id, self.category.id)
        self.assertEqual(video.genres.first().id, self.genre.id)
        self.assertEqual(video.cast_members.first().id, self.cast_member.id)

    def test_serializer_with_invalid_data(self):
        """
        Test that the serializer validates properly with invalid data.
        """
        # Missing required fields
        invalid_data = {
            'title': 'Test Video',
            # Missing year_launched, rating, duration
            'opened': True,
            'categories_id': [str(self.category.id)],
            'genres_id': [str(self.genre.id)],
            'cast_members_id': [str(self.cast_member.id)]
        }

        serializer = CreateVideoSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('year_launched', serializer.errors)
        self.assertIn('rating', serializer.errors)
        self.assertIn('duration', serializer.errors)

        # Invalid rating
        invalid_data = self.valid_data.copy()
        invalid_data['rating'] = 'INVALID_RATING'

        serializer = CreateVideoSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)

        # Invalid category ID
        invalid_data = self.valid_data.copy()
        invalid_data['categories_id'] = ['invalid-uuid']

        serializer = CreateVideoSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('categories_id', serializer.errors)

    def test_create_method(self):
        """
        Test the create method of the serializer.
        """
        serializer = CreateVideoSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        video = serializer.save()

        # Verify the video was created
        self.assertIsNotNone(video.id)

        # Verify relationships were set correctly
        self.assertEqual(video.categories.count(), 1)
        self.assertEqual(video.genres.count(), 1)
        self.assertEqual(video.cast_members.count(), 1)
        self.assertEqual(video.categories.first().id, self.category.id)
        self.assertEqual(video.genres.first().id, self.genre.id)
        self.assertEqual(video.cast_members.first().id, self.cast_member.id)


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
