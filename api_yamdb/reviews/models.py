from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin')
    )

    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.username


class CommonInfo(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class CommonInfoCategoryGenre(models.Model):
    slug = models.SlugField(unique=True)

    class Meta:
        abstract = True


class Category(CommonInfo, CommonInfoCategoryGenre):

    class Meta(CommonInfo.Meta):
        verbose_name = 'category'


class Genre(CommonInfo, CommonInfoCategoryGenre):

    class Meta(CommonInfo.Meta):
        verbose_name = 'genre'


def validate_max_year(value):
    if value <= date.today().year:
        return value
    else:
        raise ValidationError('Введите год произведения, не больше текущего.')


class Title(CommonInfo):
    year = models.SmallIntegerField(
        validators=[validate_max_year]
    )
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='titles'
    )

    class Meta(CommonInfo.Meta):
        verbose_name = 'title'


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.PROTECT
    )


class ReviewCommentBaseModel(models.Model):
    text = models.TextField('Текст', help_text='Текст отзыва')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-pub_date']


class Review(ReviewCommentBaseModel):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    score = models.IntegerField('Оценка', validators=[
        MinValueValidator(1),
        MaxValueValidator(10)
    ], help_text="Введите целое число от 1 до 10.")

    class Meta(ReviewCommentBaseModel.Meta):
        default_related_name = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_for_title')
        ]


class Comment(ReviewCommentBaseModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               verbose_name='Отзыв')

    class Meta(ReviewCommentBaseModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
