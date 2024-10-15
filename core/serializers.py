from rest_framework import serializers

from .models import CommentModel


class LikeToggleSerializer(serializers.Serializer):
    blog_id = serializers.IntegerField()
    

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['id', 'text', 'parent']

    def create(self, validated_data):
        return CommentModel.objects.create(**validated_data)

