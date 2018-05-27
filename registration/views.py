from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils import timezone
from django.views import generic

from .forms import ProfileForm
from .models import Course, CourseUser, Exam, ExamRegistration, User


@login_required
def index(request):
    """
    Displays the home page, with all courses the user is enrolled in. If
    the user is not authenticated, displays an error message.
    """
    course_user_list = CourseUser.objects.filter(
            user=request.user.id)
    return render(request, 'registration/index.html', {
        'course_user_list': course_user_list,
    })


@login_required
def profile(request):
    user = get_object_or_404(User, pk=request.user.id)

    if request.method == 'POST':
        # Populate form with request data
        form = ProfileForm(request.POST, instance=user)

        # Check for validity
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('registration:profile'))

    else:
        # Create default form
        form = ProfileForm(instance=user)

    return render(request, 'registration/profile.html', {
        'form': form,
        'current_timezone': timezone.get_current_timezone_name(),
    })


@login_required
def course_detail(request, course_code):
    course = get_object_or_404(Course,
            code=course_code)
    course_user = get_object_or_404(CourseUser,
            user=request.user.id, course=course)
    return render(request, 'registration/course_detail.html', {
        'course': course,
        'course_user': course_user,
    })


@login_required
def exam_detail(request, course_code, exam_id):
    exam = get_object_or_404(Exam,
            pk=exam_id, course__code=course_code)
    exam_reg = get_object_or_404(ExamRegistration,
            course_user__user=request.user.id, exam=exam)

    return render(request, 'registration/exam_detail.html', {
        'exam': exam,
        'exam_reg': exam_reg,
    })
