from rest_framework import serializers


class RecipientSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=200,
        allow_blank=False
    )

    course = serializers.CharField(
        max_length=200,
        allow_blank=False
    )


class GenerationJobSerializer(serializers.Serializer):
    recipients = RecipientSerializer(
        many=True,
        allow_empty=False
    )