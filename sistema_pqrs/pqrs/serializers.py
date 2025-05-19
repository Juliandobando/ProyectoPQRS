# pqrs/serializers.py

from rest_framework import serializers
from .models import PQRS

class PQRSSerializer(serializers.ModelSerializer):
    class Meta:
        model = PQRS
        fields = '__all__'  # Incluye todos los campos del modelo
