from rest_framework import serializers
from .models import CastMember, CastMemberType
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

class CastMemberSerializer(BaseSerializer):
    type = CastMemberTypeField()

    class Meta:
        model = CastMember
        fields = ['id', 'name', 'type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
