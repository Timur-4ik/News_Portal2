from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime
from .models import Post, Appointment, Category, Author
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
from .models import Post, Author
from django.views.generic.edit import CreateView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



def posts_last_24_hours(author):
    time_threshold = timezone.now() - timedelta(days=1)
    return Post.objects.filter(author=author, dateCreation__gte=time_threshold).count()



class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    template_name = 'post_edit.html'
    form_class = PostForm
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        # Получаем текущего автора
        try:
            author = Author.objects.get(authorUser=self.request.user)
        except Author.DoesNotExist:
            return HttpResponseForbidden("Автор не найден.")
        print(f"Автор найден: {author}")

        # Проверка лимита публикаций за последние 24 часа
        time_threshold = timezone.now() - timedelta(hours=24)
        recent_posts_count = Post.objects.filter(author=author, time_creation__gte=time_threshold).count()
        print(f"Количество публикаций за последние 24 часа: {recent_posts_count}")

        if recent_posts_count >= 10:
            print("Лимит публикаций за сутки превышен.")
            form.add_error(None, "Вы можете публиковать не более 3 статей в сутки.")
            return self.form_invalid(form)

        # Связываем автора с постом
        form.instance.author = author
        print(f"Связанный автор для поста: {form.instance.author}")

        # Сохраняем пост
        post = form.save()
        print(f"Пост сохранен с ID: {post.id}")

        # Получаем выбранные категории
        categories = form.cleaned_data.get('post_category')
        if categories:
            print(f"Категории для поста: {categories}")
            # Устанавливаем связи с категориями
            post.post_category.set(categories)
            print("Связи с категориями установлены.")
            post.save()  # Перезаписываем пост с новыми связями
            print(f"Количество категорий, связанных с постом: {post.post_category.count()}")
        else:
            print("Категории не были выбраны.")

        print("=== Завершение form_valid ===")
        return redirect(self.success_url)

    def test_func(self):
        # Проверка, что пользователь в группе 'authors'
        return self.request.user.groups.filter(name='authors').exists()


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.subscribers.add(request.user)
        # После подписки перенаправляем, например, на страницу категории
        return redirect('podpiska', pk=category_id)
    else:
        return HttpResponseForbidden("Нельзя подписаться через GET-запрос")

@login_required
def subscribe_unsubscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        # Удаляем подписку
        category.subscribers.remove(request.user)
        # Можно перенаправить или показать сообщение
        return redirect(request.META.get('HTTP_REFERER', 'post_list'))
    else:
        return HttpResponseForbidden("Нельзя выполнить через GET-запрос")

def subscribe_success(request, pk):
    return render(request, 'podpiska.html')


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'make_appointment.html')

    def post(self, request, *args, **kwargs):
        # Получаем данные из формы
        author = request.POST.get('author')
        text = request.POST.get('text')
        time_creation_str = request.POST.get('time_creation')

        # Парсим дату
        try:
            date_obj = datetime.strptime(time_creation_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'make_appointment.html', {'error': 'Неверный формат даты'})

        # Создаем объект Appointment
        appointment = Appointment(
            time_creation=date_obj,
            author=author,
            text=text,
        )
        appointment.save()

        # Генерируем HTML для письма
        html_content = render_to_string(
            'appointment_created.html',
            {
                'appointment': appointment,
            }
        )

        # Отправляем письмо
        email_subject = f'{appointment.author} {appointment.time_creation.strftime("%Y-%m-%d")}'
        email_body = appointment.text

        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=email_body,
            from_email='tima89063218804@yandex.ru',
            to=['t1i2m3y4r564@gmail.com'],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # Перенаправляем обратно на страницу формы
        return redirect('make_appointment')  # название URL по имени
#new email
class PostList(ListView):
    model = Post
    user = 'name'

    template_name = 'post.html'

    context_object_name = 'post'
    queryset = Post.objects.order_by('-time_creation')
    paginate_by = 10 # вот так мы можем указать количество записей на странице


    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class PostDetail(DetailView):
    template_name = 'post_detail.html'
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        categories = self.object.post_category.all()
        if user.is_authenticated:
            # Получаем список ID категорий, на которые подписан пользователь
            user_subscriptions = categories.filter(subscribers=user).values_list('id', flat=True)
        else:
            user_subscriptions = []
        context['user_subscriptions'] = list(user_subscriptions)
        return context

class NewsCreateView(PostCreate):
    def form_valid(self, form):
        form.instance.category_type = 'NW'
        return super().form_valid(form)


class ArticleCreateView(PostCreate):
    def form_valid(self, form):
        form.instance.category_type = 'AR'
        return super().form_valid(form)

class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')

class NewsUpdateView(PostUpdate):
    def form_valid(self, form):
        form.instance.category_type = 'NW'
        return super().form_valid(form)

class ArticleUpdateView(PostUpdate):
    def form_valid(self, form):
        form.instance.category_type = 'AR'
        return super().form_valid(form)

class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'news'
    ordering = ['-time_creation']
    success_url = reverse_lazy('post_list')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context
