from django.shortcuts import render
from django.views import generic
from .models import CourseUser


def index(request):
    """
    Displays the home page, with all courses the user is enrolled in. If
    the user is not authenticated, displays an error message.
    """
    if request.user.is_authenticated:
        course_user_list = CourseUser.objects.filter(
                user=request.user.id)
        return render(request, 'registration/index.html', {
            'course_user_list': course_user_list,
        })

    else:
        return render(request, 'registration/auth_failure.html', {
            'remote_user': request.META.get('REMOTE_USER', None),
        })
