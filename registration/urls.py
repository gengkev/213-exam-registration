from django.urls import path

from . import views

app_name = 'registration'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('courses/<course_code>/',
        views.course_detail, name='course-detail'),
    path('courses/<course_code>/edit/',
        views.course_edit, name='course-edit'),
    path('courses/<course_code>/sudo/',
        views.course_sudo, name='course-sudo'),

    # Course users
    path('courses/<course_code>/users/',
        views.course_users, name='course-users'),
    path('courses/<course_code>/users/import/',
        views.course_users_import, name='course-users-import'),
    path('courses/<course_code>/users/create/',
        views.course_users_create, name='course-users-create'),
    path('courses/<course_code>/users/<int:course_user_id>/',
        views.course_users_edit, name='course-users-edit'),

    # Exams
    path('courses/<course_code>/exams/<int:exam_id>/',
        views.exam_detail, name='exam-detail'),
    path('courses/<course_code>/exams/<int:exam_id>/edit/',
        views.exam_edit, name='exam-edit'),
    path('courses/<course_code>/exams/<int:exam_id>/signups/',
        views.exam_signups, name='exam-signups'),
]
