from rest_framework import serializers
from .models import FoundItem, LostItem
from django.contrib.auth import get_user_model

User = get_user_model()

class FoundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundItem
        fields = [
            'id', 'submitter', 'photo', 'brand', 'color', 'size',
            'unique_identifiers', 'description', 'location',
            'latitude', 'longitude', 'found_date', 'found_time',
            'storage_location', 'date_submitted', 'is_resolved',
            'status', 'scheduled_donation_date'
        ]
        read_only_fields = ['submitter', 'date_submitted', 'status']

    def create(self, validated_data):
        # Set the submitter to the current user
        validated_data['submitter'] = self.context['request'].user
        return super().create(validated_data)

class LostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostItem
        fields = [
            'id', 'submitter', 'photo', 'brand', 'color', 'size',
            'unique_identifiers', 'description', 'location',
            'latitude', 'longitude', 'lost_date', 'lost_time',
            'contact_reward', 'date_submitted', 'is_resolved', 'status'
        ]
        read_only_fields = ['submitter', 'date_submitted', 'status']

    def create(self, validated_data):
        # Set the submitter to the current user
        validated_data['submitter'] = self.context['request'].user
        return super().create(validated_data)
