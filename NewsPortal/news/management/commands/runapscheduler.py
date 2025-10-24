import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from django.urls import reverse

from myapp.models import Post, Category

logger = logging.getLogger(__name__)


# ваша текущая задача
def my_job():
    send_mail(
        'Job mail',
        'hello from job!',
        from_email='tima89063218804@yandex.ru',
        recipient_list=['t1i2m3y4r564@gmail.com'],
    )


# задача по очистке старых заданий
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


# новая функция для рассылки новостей
def send_weekly_newsletter():
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(time_creation__gte=one_week_ago)

    categories = Category.objects.all()

    for category in categories:
        subscribers = category.subscribers.all()

        posts_in_category = recent_posts.filter(post_category=category).distinct()

        if not posts_in_category.exists():
            continue

        # создаем список гиперссылок
        post_links = ""
        for post in posts_in_category:
            url = f"{settings.SITE_URL}{reverse('post_detail', args=[post.id])}"
            post_links += f"<a href='{url}'>{post.title}</a><br>"

        # отправляем письмо каждому подписчику
        for user in subscribers:
            send_mail(
                subject='Weekly News from Your Subscribed Categories',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=f"<h2>New articles for you:</h2>{post_links}"
            )


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # текущая задача
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        # задача по очистке старых задач
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="0", minute="0"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly delete_old_job_executions.")

        # добавляем задачу для рассылки новостей
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(day_of_week='sun', hour='8', minute='0'),  # каждое воскресенье в 8 утра
            id='weekly_newsletter',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly newsletter job.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")