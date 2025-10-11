from django_filters import FilterSet, DateFilter
from django.forms.widgets import DateInput
from .models import Post
import django_filters


class PostFilter(FilterSet):
    time_creation = DateFilter(
        field_name='time_creation',
        lookup_expr='gte',  # Ищем даты, начиная с указанной
        widget=DateInput(attrs={'type': 'date'}),
        label='Date'
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],  # Поиск по части названия
            'author': ['exact'],  # фильтр по автору
        }