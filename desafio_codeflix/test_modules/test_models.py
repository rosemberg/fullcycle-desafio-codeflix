from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import CastMember, CastMemberType, Category, Genre, Video, Rating, AudioVideoMedia, MediaStatus
from ..serializers import CreateVideoSerializer
from ..test_utils import JWTAuthMixin
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