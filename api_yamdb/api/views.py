import random

from core.views import CreateListDestroyModelMixinSet
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly
from .serializers import (CategorySerializer, CommentsSerializer,
                          EditProfileSerializer, GenreSerializer,
                          ReadTitleSerializer, RegistrationSerializer,
                          ReviewsSerializer, TokenSerializer, UserSerializer,
                          WriteTitleSerializer)

OK = 200
BAD_REQUEST = 400
METHOD_NOT_ALLOWED = 405

BAD_REQUEST_MESSAGE = ('В базе данных уже есть пользователь '
                       'с таким "username" или "email"')


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    paginathion_class = (LimitOffsetPagination,)
    permission_classes = (IsAdmin,)

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
        serializer_class=EditProfileSerializer)
    def get_and_edit_self_profile(self, request):
        """Получение и редактирование профиля."""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=OK)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True, )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    """Регистрация пользователя и восстановление секретного кода."""
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = random.randint(1000, 9999)
    try:
        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
        )
    except IntegrityError:
        return Response(BAD_REQUEST_MESSAGE, status=BAD_REQUEST)
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        subject='Registration.',
        message=f'Your code: {confirmation_code}',
        recipient_list=[user.email],
        fail_silently=False,
    )
    return Response(serializer.data, status=OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получение токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = generics.get_object_or_404(
        User, username=serializer.validated_data['username'])
    if (user.confirmation_code
            == serializer.validated_data['confirmation_code']):
        token = RefreshToken.for_user(user)
        return Response(
            {'token': str(token.access_token)}, status=OK)
    return Response(serializer.errors, status=BAD_REQUEST)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    paginathion_class = (LimitOffsetPagination,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = TitleFilter
    search_fields = ('name',)
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadTitleSerializer
        return WriteTitleSerializer


class CategoriesGenresViewSet(CreateListDestroyModelMixinSet):
    permission_classes = (IsAdminOrReadOnly,)
    paginathion_class = (LimitOffsetPagination,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    class Meta:
        abstract = True


class CategoriesViewSet(CategoriesGenresViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(CategoriesGenresViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_title(self, id=None):
        return generics.get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('text',)

    def get_review(self):
        return generics.get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=ReviewsViewSet.get_title(
                self, id=self.kwargs.get('title_id')
            )
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
