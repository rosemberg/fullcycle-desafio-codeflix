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
