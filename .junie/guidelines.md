# Codeflix Project Development Guidelines

This document provides guidelines and instructions for developing and testing the Codeflix project.

## Build/Configuration Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setting Up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fullcycle-desafio-codeflix
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Testing Information

### Running Tests

To run all tests:
```bash
python manage.py test
```

To run tests for a specific app:
```bash
python manage.py test desafio_codeflix
```

To run a specific test class:
```bash
python manage.py test desafio_codeflix.tests.VideoModelTest
```

To run a specific test method:
```bash
python manage.py test desafio_codeflix.tests.VideoModelTest.test_video_creation
```

### Writing Tests

The project uses Django's testing framework along with Django REST Framework's testing utilities for API tests.

#### Model Tests

For testing models, extend `django.test.TestCase`:

```python
from django.test import TestCase
from desafio_codeflix.models import Video

class VideoModelTest(TestCase):
    def setUp(self):
        # Create test data
        Video.objects.create(
            title="Test Video",
            description="This is a test video",
            url="https://example.com/video"
        )
    
    def test_video_creation(self):
        # Test the model
        video = Video.objects.get(title="Test Video")
        self.assertEqual(video.description, "This is a test video")
```

#### API Tests

For testing API endpoints, extend `rest_framework.test.APITestCase`:

```python
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from desafio_codeflix.models import Video

class VideoAPITest(APITestCase):
    def setUp(self):
        # Create test data
        self.video = Video.objects.create(
            title="API Test Video",
            description="This is a test video for API",
            url="https://example.com/api-video"
        )
        self.list_url = reverse('video-list')
        
    def test_list_videos(self):
        # Test GET request
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Additional Development Information

### Project Structure

- **fullcycle_desafio_codeflix/**: Main project directory
  - **settings.py**: Project settings
  - **urls.py**: Main URL configuration
- **desafio_codeflix/**: Main application
  - **models.py**: Data models
  - **views.py**: API views and serializers
  - **urls.py**: Application URL configuration
  - **tests.py**: Tests for the application

### API Endpoints

The API follows RESTful conventions:

- **GET /api/videos/**: List all videos
- **POST /api/videos/**: Create a new video
- **GET /api/videos/{id}/**: Retrieve a specific video
- **PUT /api/videos/{id}/**: Update a specific video
- **DELETE /api/videos/{id}/**: Delete a specific video

### Code Style

- Follow PEP 8 guidelines for Python code
- Use 4 spaces for indentation
- Use meaningful variable and function names
- Include docstrings for classes and methods
- Keep lines under 100 characters when possible

### Django REST Framework

The project uses Django REST Framework for building APIs:

- Use ViewSets for CRUD operations on models
- Use Serializers to convert between complex data types and Python datatypes
- Use Routers to automatically generate URL patterns for ViewSets

### Database Migrations

When making changes to models:

1. Create migrations:
   ```bash
   python manage.py makemigrations
   ```

2. Apply migrations:
   ```bash
   python manage.py migrate
   ```

3. If needed, create a data migration:
   ```bash
   python manage.py makemigrations --empty desafio_codeflix --name data_migration_name
   ```