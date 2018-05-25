from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Course, CourseUser, Exam, ExamRegistration


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


# TODO: Require login
def course_detail(request, course_code):
    course = get_object_or_404(Course,
            code=course_code)
    course_user = get_object_or_404(CourseUser,
            user=request.user.id, course=course)
    return render(request, 'registration/course_detail.html', {
        'course': course,
        'course_user': course_user,
    })


# TODO: Require login
def exam_detail(request, course_code, exam_id):
    exam = get_object_or_404(Exam,
            pk=exam_id, course__code=course_code)
    exam_reg = get_object_or_404(ExamRegistration,
            course_user__user=request.user.id, exam=exam)

    return render(request, 'registration/exam_detail.html', {
        'exam': exam,
        'exam_reg': exam_reg,
    })
