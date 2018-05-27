from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import (
    require_http_methods, require_safe, require_POST
)

from .forms import ProfileForm, ExamRegistrationForm
from .models import Course, CourseUser, Exam, ExamRegistration, User


@require_safe
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


@require_http_methods(['GET', 'HEAD', 'POST'])
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


@require_safe
@login_required
def course_detail(request, course_code):
    course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        course__code=course_code
    )
    return render(request, 'registration/course_detail.html', {
        'course': course_user.course,
        'course_user': course_user,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def exam_detail(request, course_code, exam_id):
    exam_reg = get_object_or_404(
        ExamRegistration,
        course_user__user=request.user.id,
        exam=exam_id,
        exam__course__code=course_code
    )

    if request.method == 'POST':
        # Populate form with request data
        form = ExamRegistrationForm(request.POST, instance=exam_reg)

        # Check for validity
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'registration:exam-detail',
                args=[exam_reg.exam.course.code, exam_reg.exam.id],
            ))

    else:
        # Create default form
        form = ExamRegistrationForm(instance=exam_reg)

    return render(request, 'registration/exam_detail.html', {
        'form': form,
        'exam': exam_reg.exam,
        'exam_reg': exam_reg,
    })
