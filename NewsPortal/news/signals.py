from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from .models import Post

@receiver(m2m_changed, sender=Post.post_category.through)
def send_notification_on_new_post(sender, instance, action, reverse, model, pk_set, **kwargs):
    print("==== Отладка сигнала ====")
    print(f"Действие: {action}")
    print(f"Объект: {instance}")
    print(f"Реверс: {reverse}")
    print(f"Модель: {model}")
    print(f"PK набор: {pk_set}")

    # Проверяем, что сработало именно при добавлении категорий
    if action == 'post_add':
        post = instance
        print(f"Обработка поста с ID: {post.id}")

        # Формируем полный URL для поста
        domain = Site.objects.get_current().domain
        full_url = f"http://{domain}{post.get_absolute_url()}"
        print(f"Полный URL поста: {full_url}")

        try:
            categories = post.post_category.all()
            print(f"Обработка {categories.count()} категорий(и)")
        except Exception as e:
            print(f"Ошибка при получении категорий поста: {e}")
            categories = []

        for category in categories:
            print(f"Обработка категории: {category.name}")

            try:
                subscribers = category.subscribers.all()
                print(f"Количество подписчиков: {subscribers.count()}")
            except Exception as e:
                print(f"Ошибка при получении подписчиков для категории {category.name}: {e}")
                continue

            for user in subscribers:
                print(f"Отправка письма пользователю: {user.email}")
                try:
                    email = EmailMultiAlternatives(
                        subject=f'Новый пост в категории {category.name}',
                        from_email='tima89063218804@yandex.ru',
                        to=[user.email],
                    )
                    html_content = render_to_string(
                        'appointment_created.html',  # ваш шаблон
                        {
                            'post': post,
                            'user': user,
                            'post_url': full_url,
                        }
                    )
                    print(f"Формируемый полный URL: {full_url}")
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    print(f"Письмо успешно отправлено {user.email}")
                except Exception as e:
                    print(f"Ошибка при отправке письма {user.email}: {e}")

    else:
        print(f"Действие {action} не обрабатывается.")