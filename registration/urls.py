from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('', views.index, name='index'),
    path('exams/<int:exam_id>/', views.exam_detail, name='exam-detail'),
]
