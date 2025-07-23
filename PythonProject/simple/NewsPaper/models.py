from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import truncatewords


# создаем модель автора
class Author(models.Model):
    # рейтинг пользователя
    user_rate = models.IntegerField(default=0)
    # связь один к одному с User, при удалении автора, удалится и связанный с ним юзер
    author = models.OneToOneField(User, on_delete=models.CASCADE)

    # обновить рейтинг автора
    def update_rating(self):
        # суммарный рейтинг всех комментариев к статьям
        sum_rating = self.post_set.aggregate(post_rating=Sum('post_rate'))
        result_sum_rating = 0
        try:
            result_sum_rating += sum_rating.get('post_rating')
        except TypeError:
            result_sum_rating = 0

        # суммарный рейтинг всех комментариев самого автора
        sum_comment_rating = self.author.comment_set.aggregate(comment_rating=Sum('comment_rate'))
        result_sum_comment_rating = 0
        result_sum_comment_rating += sum_comment_rating.get('comment_rating')

        # суммарный рейтинг каждой статьи автора умноженный на 3
        self.user_rate = result_sum_rating * 3 + result_sum_comment_rating
        # сохраняем результаты в базу данных
        self.save()


# создаем модель категории статьи/новости
class Category(models.Model):
    # категории статей/новостей - темы, которые они отражают (спорт, политика, образование и т. д.)
    # данное поле делаем уникальным
    article_category = models.CharField(max_length=255, unique=True)


# создаем модель пост
class Post(models.Model):
    # связь один ко многим с Author
    post_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    # связь многие ко многим с Category
    post_category = models.ManyToManyField(Category)

    """ <<< Настройка выбора категории поста >>> """
    # варианты для поля с выбором (статья или новость)
    article = 'A'
    news = 'N'

    POSITIONS = [
        (article, "Статься"),
        (news, "Новость"),
    ]

    # выбор категории поста (статья или новость), длина символа = 1, по умолчанию = "Новость"
    category = models.CharField(max_length=1,
                                choices=POSITIONS,
                                default=news)
    """ <<< Конец настройки выбора категории поста >>> """

    # дата и время создания поста
    date_created = models.DateField(auto_now_add=True)

    # заголовок статьи/новости
    title = models.CharField(max_length=50)

    # текст статьи/новости
    content = models.TextField()

    """ <<< Рейтинг >>> """
    # рейтинг статьи/новости
    post_rate = models.IntegerField(default=0)

    # метод, увеличивающий рейтин на единицу
    def like(self):
        self.post_rate += 1
        # сохранение значения в базу данных
        self.save()

    # метод, уменьшающий рейтин на единицу
    def dislike(self):
        self.post_rate -= 1
        # сохранение значения в базу данных
        self.save()

    # предварительный просмотр статьи (превью 124 символов статьи)
    def preview(self):
        return self.content[:125]

    # формат вывода наименования товара и его описания (первые 20 знаков)
    def __str__(self):
        return f'{self.title.title()}: {self.content[:20]}'


# создаем промежуточную модель PostCategory
class PostCategory(models.Model):
    # связь «один ко многим» с моделью Post
    post_category = models.ForeignKey(Post, on_delete=models.CASCADE)
    # связь «один ко многим» с моделью Category
    category_category = models.ManyToManyField(Category)


# создаем модель Comment, чтобы можно было под каждой новостью/статьей оставлять комментарии
class Comment(models.Model):
    # связь «один ко многим» с моделью Post
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # связь «один ко многим» с встроенной моделью User (комментарии может оставить любой пользователь)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE)

    feedback_text = models.TextField()

    comment_date_created = models.DateField(auto_now_add=True)

    comment_rate = models.IntegerField(default=0)

    def like(self):
        self.comment_rate += 1
        self.save()

    def dislike(self):
        self.comment_rate -= 1
        self.save()
