from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import CastMember, CastMemberType, Category, Genre, Video, Rating, AudioVideoMedia, MediaStatus
from ..serializers import CreateVideoSerializer
from ..test_utils import JWTAuthMixin
import time

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