from rest_framework import serializers

from .models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    investor = serializers.StringRelatedField(read_only=True)
    investor_id = serializers.UUIDField(source="investor.id", read_only=True)

    class Meta:
        model = Investment
        fields = [
            "id",
            "startup",
            "investor",
            "investor_id",
            "amount",
            "status",
            "note",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "startup",
            "investor",
            "investor_id",
            "status",
            "created_at",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Investitsiya summasi 0 dan katta bo'lishi kerak.")
        return value
