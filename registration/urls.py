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

    # GitHub authorization
    path('courses/<course_code>/github/landing/',
        views.course_github_landing, name='course-github-landing'),
    path('courses/<course_code>/github/authorize/',
        views.course_github_authorize, name='course-github-authorize'),
    path('courses/<course_code>/github/deauthorize/',
        views.course_github_deauthorize, name='course-github-deauthorize'),
    path('courses/<course_code>/github/callback/',
        views.course_github_callback, name='course-github-callback'),
    path('courses/<course_code>/github/info/<username>/',
        views.course_github_info, name='course-github-info'),

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
    path('courses/<course_code>/exams/<int:exam_id>/signups/csv/',
        views.exam_signups_csv, name='exam-signups-csv'),
    path('courses/<course_code>/exams/<int:exam_id>/signups/counts/',
        views.exam_signups_counts, name='exam-signups-counts'),
    path('courses/<course_code>/exams/<int:exam_id>/signups/<username>/',
        views.exam_signups_detail, name='exam-signups-detail'),
    path('courses/<course_code>/exams/<int:exam_id>/signups/<username>/checkin',
        views.exam_signups_checkin, name='exam-signups-checkin'),
    path('courses/<course_code>/exams/<int:exam_id>/signups/<username>/checkout',
        views.exam_signups_checkout, name='exam-signups-checkout'),

]
