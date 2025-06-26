from rest_framework import serializers
from .models import CastMember, CastMemberType, Category, Genre, Video, Rating, AudioVideoMedia, MediaStatus
from .base import BaseSerializer

class CastMemberTypeField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        # Utilizamos o "choices" do DRF, que permite um conjunto de opções limitado para um certo campo.
        choices = [(type.name, type.value) for type in CastMemberType]
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        # Valor vindo da API como "str" é convertido para o StrEnum
        return CastMemberType(super().to_internal_value(data))

    def to_representation(self, value):
        # O valor vindo do nosso domínio é convertido para uma string na API
        return str(super().to_representation(value))

class RatingField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        choices = [(rating.name, rating.value) for rating in Rating]
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        return Rating(super().to_internal_value(data))

    def to_representation(self, value):
        return str(super().to_representation(value))

class MediaStatusField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        choices = [(status.name, status.value) for status in MediaStatus]
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        return MediaStatus(super().to_internal_value(data))

    def to_representation(self, value):
        return str(super().to_representation(value))

class CastMemberSerializer(BaseSerializer):
    type = CastMemberTypeField()

    class Meta:
        model = CastMember
        fields = ['id', 'name', 'type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CategorySerializer(BaseSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class GenreSerializer(BaseSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'is_active', 'categories', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AudioVideoMediaSerializer(BaseSerializer):
    status = MediaStatusField()

    class Meta:
        model = AudioVideoMedia
        fields = ['id', 'file_path', 'encoded_path', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class VideoSerializer(BaseSerializer):
    rating = RatingField()
    video = AudioVideoMediaSerializer(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'year_launched', 'opened', 
            'rating', 'duration', 'categories', 'genres', 'cast_members',
            'video', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CreateVideoSerializer(BaseSerializer):
    rating = RatingField()
    categories_id = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    genres_id = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    cast_members_id = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'year_launched', 'opened', 
            'rating', 'duration', 'categories_id', 'genres_id', 'cast_members_id'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        categories_id = validated_data.pop('categories_id', [])
        genres_id = validated_data.pop('genres_id', [])
        cast_members_id = validated_data.pop('cast_members_id', [])

        video = Video.objects.create(**validated_data)

        if categories_id:
            video.categories.set(Category.objects.filter(id__in=categories_id))

        if genres_id:
            video.genres.set(Genre.objects.filter(id__in=genres_id))

        if cast_members_id:
            video.cast_members.set(CastMember.objects.filter(id__in=cast_members_id))

        return video

class UploadVideoMediaSerializer(BaseSerializer):
    file_path = serializers.CharField(max_length=255)

    class Meta:
        model = AudioVideoMedia
        fields = ['file_path']

    def create(self, validated_data):
        video_id = self.context.get('video_id')
        if not video_id:
            raise serializers.ValidationError("Video ID is required")

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            raise serializers.ValidationError("Video not found")

        # Create the media object
        media = AudioVideoMedia.objects.create(**validated_data)

        # Associate it with the video
        video.video = media
        video.save()

        return media
