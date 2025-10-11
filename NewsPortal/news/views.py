from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from .models import Post, Appointment
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
    success_url = reverse_lazy('post_list')

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    template_name = 'post_edit.html'
    form_class = PostForm
    success_url = reverse_lazy('post_list')

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
