from django.db import models
import uuid
from enum import StrEnum

# Create your models here.
class CastMemberType(StrEnum):
    DIRECTOR = "DIRECTOR"
    ACTOR = "ACTOR"

class CastMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=8,
        choices=[(type.name, type.value) for type in CastMemberType]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, related_name='genres')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Rating(StrEnum):
    L = "L"
    AGE_10 = "10"
    AGE_12 = "12"
    AGE_14 = "14"
    AGE_16 = "16"
    AGE_18 = "18"

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    year_launched = models.IntegerField()
    opened = models.BooleanField(default=False)
    rating = models.CharField(
        max_length=10,
        choices=[(rating.name, rating.value) for rating in Rating]
    )
    duration = models.IntegerField()
    categories = models.ManyToManyField(Category, related_name='videos')
    genres = models.ManyToManyField(Genre, related_name='videos')
    cast_members = models.ManyToManyField(CastMember, related_name='videos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
