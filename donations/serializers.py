from rest_framework import serializers

from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.StringRelatedField(read_only=True)
    donor_id = serializers.UUIDField(source="donor.id", read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "startup",
            "donor",
            "donor_id",
            "amount",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "startup", "donor", "donor_id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Donation summasi 0 dan katta bo'lishi kerak.")
        return value
