from django.urls import path
from .views import PostList, PostDetail, PostDelete, PostSearch, NewsCreateView, ArticleCreateView, NewsUpdateView, ArticleUpdateView, AppointmentView, subscribe_to_category, subscribe_success, subscribe_unsubscribe

urlpatterns = [
    path('', PostList.as_view(), name = 'post_list'),
    path('<int:pk>', PostDetail.as_view(), name = 'post_detail'),
    path('news/create/', NewsCreateView.as_view(), name='post_create'),

    path('news/<int:pk>/edit/', NewsUpdateView.as_view(), name='post_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('news/search/', PostSearch.as_view(), name='post_search'),

    path('articles/create/', ArticleCreateView.as_view(), name='articles_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='articles_edit'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),

    path('appointment/', AppointmentView.as_view(), name='make_appointment'),
    path('category/<int:category_id>/subscribe/', subscribe_to_category, name='subscribe_to_category'),
    path('category/<int:pk>/subscribe/success/', subscribe_success, name='podpiska'),
    path('category/<int:category_id>/unsubscribe/', subscribe_unsubscribe, name='unsubscribe_from_category'),
]
