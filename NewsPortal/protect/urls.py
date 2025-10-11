from django.urls import path
from .views import IndexView

urlpatterns = [
    path('LK/', IndexView.as_view()),
]