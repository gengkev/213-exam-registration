from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('courses/<course_code>/',
        views.course_detail, name='course-detail'),
    path('courses/<course_code>/exams/<int:exam_id>/',
        views.exam_detail, name='exam-detail'),
]
