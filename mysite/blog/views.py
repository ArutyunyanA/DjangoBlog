from django.shortcuts import render
from django.http import Http404
from .models import Post, Comment
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag


"""
В данном представлении извлекаются все посты со статусом PUBLISHED, 
используя менеджер published, который мы создали ранее.
Наконец, мы используем функцию сокращенного доступа1 render(), 
предоставляемую Django, чтобы прорисовать список постов заданным шаблоном. 
Указанная функция принимает объект request, путь к шаблону и контекстные
переменные, чтобы прорисовать данный шаблон. Она возвращает объект HttpResponse 
с прорисованным текстом (обычно исходным кодом HTML).

class PostListViews(ListView):
    # Алтернативное представление списка постов
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
    

"""
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags_in=[tag])
    # pagination list for 3 posts on a page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page_number не целое число, то 
        # выдать первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если page_number находится вне диапазона, то 
        # выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(
        request, 
        'blog/post/list.html',
        {'posts': posts, 'tag': tag}
    )

"""
Указанное представление принимает аргумент id поста. Здесь мы пытаемся извлечь объект 
Post с заданным id, вызвав метод get() стандартного менеджера objects. Мы создаем исключение 
Http404, чтобы вернуть ошибку HTTP с кодом состояния, равным 404, если возникает исключение 
DoesNotExist, то есть модель не существует, поскольку результат не найден.
"""

def post_share(request, post_id):
    # Извлечь пост по идентификатору id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
    # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
        # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recomends you to read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s commments: {cd['comments']}"
            send_mail(subject, message, 'your@accountmail.com', [cd['to']])
            sent = True
    # ... отправить электронное письмо
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
 

def post_details(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        status=Post.Status.PUBLISHED, 
        # Убираем id=id вместо этого добавляем year, month, day и post
        # чтобы использовать аргументы и извлекать опубликованный пост с заданным 
        # слагом и датой публикации.
        slug=post, 
        publish__year=year, 
        publish__month=month, 
        publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    return render(request, 'blog/post/details.html', {'post': post, 'comments': comments, 'form': form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})
