from core.mixins import ValidateMixin
from rest_framework import generics, serializers
from reviews.models import Category, Comments, Genre, Review, Title, User


class UserSerializer(ValidateMixin, serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class EditProfileSerializer(UserSerializer):
    """Сериализатор для работы с профилем пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class RegistrationSerializer(ValidateMixin, serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(required=True, max_length=150, )
    confirmation_code = serializers.CharField(required=True, )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с жанрами."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для работы с категориями."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class ReadTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка произведений."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('__all__',)


class WriteTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведения."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    def validate(self, data):
        """Валидация отзывов.

        Args:
            data (dict): словарь с данными для валидации.

        Raises:
            serializers.ValidationError: ошибка при попытке оставить более
            одного отзыва.

        Returns:
            dict: словарь с проверенными данными.
        """

        if self.context['request'].method != 'POST':
            return data
        title = generics.get_object_or_404(
            Title,
            id=self.context['request'].parser_context['kwargs'].get(
                'title_id')
        )
        if Review.objects.filter(
            title_id=title.id,
            author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError(
                detail=('На произведение можно оставить '
                        'не более одного отзыва'),
                code=400
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с комментариями."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    def validate(self, data):
        """Валидация комментариев.

        Args:
            data (dict): словарь с данными для валидации.

        Raises:
            serializers.ValidationError: ошибка при отсутсвии отзыва.

        Returns:
            dict: словарь с проверенными данными.
        """

        if self.context['request'].method != 'POST':
            return data
        title = generics.get_object_or_404(
            Title,
            id=self.context['request'].parser_context['kwargs'].get(
                'title_id')
        )
        if not Review.objects.filter(
            title_id=title.id,
            author=self.context['request'].user
        ).exists():
            raise serializers.ValidationError(
                detail=('Отзыв не найден'),
                code=400
            )
        return data

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')
