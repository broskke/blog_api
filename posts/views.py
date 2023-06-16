from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from comment.serializers import CommentSerializers
from like.serializers import LikeUserSerializer
from .models import Post
from . import serializers
from .permissions import IsAuthor, IsAuthorOrAdmin
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from like.models import Favorite

class StandartResultPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'page'


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('owner', 'category', )
    search_fields = ('title', 'body')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.PostCreateSerializer
        return serializers.PostDetailSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthorOrAdmin(), ]
        elif self.action in ('update', 'partial_update'):
            return [IsAuthor(), ]
        return [permissions.IsAuthenticatedOrReadOnly(), ]

    @action(['GET'], detail=True)
    def comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.all()
        serializer = CommentSerializers(instance=comments, many=True)
        return Response(serializer.data, status=200)

    @action(['GET'], detail=True)
    def likes(self, request, pk):
        post = self.get_object()
        likes = post.likes.all()
        serializer = LikeUserSerializer(instance=likes, many=True)
        return Response(serializer.data, status=200)
    
    @action(['POST','DELETE'], detail=True)
    def favorites(self, request, pk):
            post = self.get_object()
            user = request.user
            favorite = user.favorites.filter(post=post)
            if request.method == 'POST':
                if user.favorites.filter(post=post).exists():
                    return Response({'msg':'Already in Favorite'}, status=400)
                Favorite.objects.create(owner=user, post=post)
                return Response({'msg':'Added to Favorite'}, status=201)
            
            if favorite.exists():
                favorite.delete()
                return Response({'msg':'Deleted from Favorite'}, status=204)
            return Response({'msg': 'Post Not Found in Favorite'}, status=404)
    

# class PostListCreateView(generics.ListCreateAPIView):
#     queryset = Post.objects.all()
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return serializers.PostListSerializer
#         return serializers.PostCreateSerializer
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#
# class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.objects.all()
#
#     def get_serializer_class(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return serializers.PostCreateSerializer
#         return serializers.PostDetailSerializer
#
#     def get_permissions(self):
#         if self.request.method in ('PUT', 'PATCH'):
#             return [IsAuthor()]
#         elif self.request.method == 'DELETE':
#             return [IsAuthorOrAdmin()]
#         return [permissions.AllowAny()]
