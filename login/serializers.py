from rest_framework import serializers
from snippets.models import Snippet,LANGUAGE_CHOICE,STYLE_CHOICE
class UserSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)