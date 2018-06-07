from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('courses/<course_code>/',
        views.course_detail, name='course-detail'),
    path('courses/<course_code>/manage/',
        views.course_manage, name='course-manage'),
    path('courses/<course_code>/manage/edit/',
        views.course_manage_edit, name='course-manage-edit'),
    path('courses/<course_code>/manage/users/',
        views.course_manage_users, name='course-manage-users'),
    path('courses/<course_code>/exams/<int:exam_id>/',
        views.exam_detail, name='exam-detail'),
]
