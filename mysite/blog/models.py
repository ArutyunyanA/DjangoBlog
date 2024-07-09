from django.db import models
# Добавляем django-taggit модуль и импортируем
#from taggit.managers import TaggableManager

# Встроенный в Django ORM-преобразователь основан на итерируемых наборах запросов QuerySet. 
# Итерируемый набор запросов QuerySet – это коллекция запросов к базе данных, предназначенных 
# для извлечения объектов из базы данных.
from django.db.models.query import QuerySet
 
# модуль timezone. Метод timezone.now возвращает текущую дату/время в формате, 
# зависящем от часового пояса. Его можно трактовать как версию стандартного метода Python datetime.now с учетом часового пояса
from django.utils import timezone
# Мы импортировали модель User из модуля django.contrib.auth.models и 
# добавили в модель Post поле author.
from django.contrib.auth.models import User
# используем функцию-утилиту reverse() модуля django.urls.
from django.urls import reverse
from taggit.managers import TaggableManager


# Добавление менеджера для извлечения объектов из базы данных
# Метод get_queryset() менеджера возвращает набор запросов QuerySet, который будет исполнен
# Мы переопределили этот метод, чтобы сформировать конкретно-прикладной набор запросов QuerySet, 
# фильтрующий посты по их статусу и возвращающий поочередный набор запросов QuerySet, содержащий 
# посты только со статусом PUBLISHED.
class PublishedManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    
    # Мы определили перечисляемый класс Status путем подклассирования класса models.TextChoices.
    class Status(models.TextChoices):
        DRAFT = 'DF', 'DRAFT'
        PUBLISHED = 'PB', 'PUBLISHED'

    
    # title: поле заголовка поста. Это поле с типом CharField, которое транс- лируется в столбец VARCHAR в базе данных SQL
    title = models.CharField(max_length=250)

    # slug: поле SlugField, которое транслируется в столбец VARCHAR в базе дан- ных SQL
    # Слаг – это короткая метка, содержащая только буквы, цифры, знаки подчеркивания или дефисы. 
    # Пост с заголовком «Django Reinhardt: A legend of Jazz» мог бы содержать такой заголовок: «django-reinhardt- legend-jazz»
    slug = models.SlugField(max_length=250, unique_for_date='publish')

    # Это поле определяет взаимосвязь многие- к-одному, означающую, 
    # что каждый пост написан пользователем и пользователь может написать любое число постов.
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')

    # body: поле для хранения тела поста. Это поле с типом TextField, которое транслируется в столбец Text в базе данных SQL.
    body = models.TextField()

    # publish: поле с типом DateTimeField, которое транслируется в столбец DATETIME в базе данных SQL
    publish = models.DateTimeField(default=timezone.now)

    # created: поле с типом DateTimeField. Оно будет использоваться для хра- нения даты и времени создания поста.
    created = models.DateTimeField(auto_now_add=True)

    # updated: поле с типом DateTimeField. Оно будет использоваться для хра- нения последней даты и времени обновления поста.
    updated = models.DateTimeField(auto_now=True)

    # добавлено новое поле status, являющееся экземп- ляром типа CharField. Оно содержит параметр choices, 
    # чтобы ограничивать значение поля вариантами из Status.choices.
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    # менеджер, применяемый по умолчанию
    objects = models.Manager()

    # конкретно-прикладной менеджер
    published = PublishedManager()
    
    # Менеджер tags позволит добавлять, извлекать и удалять теги из объектов Post
    tags = TaggableManager()

    # Внутрь модели был добавлен Meta-класс. Этот класс определяет метадан- ные модели. 
    # Мы используем атрибут ordering, сообщающий Django, что он должен сортировать результаты по полю publish.
    # знак '-' перед publish означает, что посты будут сортироваться от нового к старому сверху вниз
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    """
    В модельный класс также добавлен метод __str__(). Это метод Python, который применяется по умолчанию 
    и возвращает строковый литерал с удобочитаемым представлением объекта. в Python 3 все строковые 
    литералы изначально считаются кодированными в Юникоде; по- этому мы используем только 
    метод __str__(). Раньше в Python 2использовали __unicode__()
    """
    def __str__(self):
        return self.title
    

    """
    Функция reverse() будет формировать URL-адрес динамически, применяя имя URL-адреса, 
    определенное в шаблонах URL-адресов. Мы использовали именное пространство blog, 
    за которым следуют двоеточие и URL-адрес post_detail. Напомним, что именное пространство 
    blog определяется в главном файле urls.py проекта при вставке шаблонов URL-адресов 
    из blog.urls. URL-адрес post_detail определен в файле urls.py приложения blog. 
    Результирующий строковый литерал, blog:post_detail, можно использовать глобально в проекте, 
    чтобы ссылаться на URL-адрес детальной информации о посте. Этот URL-адрес имеет обязательный 
    параметр - id извлекаемого поста блога. Идентификатор id объекта Post был включен в качестве 
    позиционного аргумента, используя параметр args=[self.id].
    """
    def get_absolute_url(self):
        return reverse('blog:post_details', args=[
            self.publish.year, 
            self.publish.month, 
            self.publish.day, 
            self.slug])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"