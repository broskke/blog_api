from rest_framework import generics, permissions
from .models import Post
from . import serializers


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.
        return serializers.