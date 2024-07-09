from django.urls import path
from . import views

app_name = 'blog'

urlpatterns =[
    # представления поста
    # Первый шаблон URL-адреса не принимает никаких 
    # аргументов и соотносится с представлением post_list
    path('', views.post_list, name='post_list'),
    # Подключаем теги
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # представления поста class ListView
    #path('', views.PostListViews.as_view(), name='post_list'),
    # Второй шаблон соотносится с представлением post_detail и принимает 
    # только один аргумент id, который совпадает с целым числом, заданным 
    # целым числом конвертора путей int это нужно исправлять.
    # Конвертор пути int используется для параметров year, month и day, 
    # тогда как конвертор пути slug применяется для параметра post
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_details, name='post_details'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment')
]

"""
Для захвата значений из URL-адреса используются угловые скобки. Любое значение, 
указанное в шаблоне URL-адреса как <parameter>, записывается в качестве строкового литерала. 
Для конкретного сопоставления и возврата целого числа используются конверторы путей, такие как 
<int:year>. Напри- мер, <slug:post> будет, в частности, совпадать со слагом (строковым литералом, 
который может содержать только буквы, цифры, подчеркивания или дефисы).
"""
