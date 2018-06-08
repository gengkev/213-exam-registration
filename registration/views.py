from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models.functions import TruncDay
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import (
    require_http_methods, require_safe, require_POST
)

from .forms import (
    ProfileForm, ExamRegistrationForm, CourseEditForm, CourseUserEditForm,
    CourseUserCreateForm
)
from .models import (
    Course, CourseUser, Exam, ExamRegistration, User
)


@require_safe
@login_required
def index(request):
    """
    Displays the home page, with all courses the user is enrolled in. If
    the user is not authenticated, displays an error message.
    """
    course_user_list = request.user.course_user_set.all()
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
            messages.success(request,
                "Your profile was updated successfully.",
            )
            return HttpResponseRedirect(reverse('registration:profile'))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = ProfileForm(instance=user)

    # Get current local time and timezone
    now = timezone.localtime()

    # Format UTC offset
    def format_seconds(n):
        hours, minutes = divmod(n // 60, 60)
        return "{:02}:{:02}".format(hours, minutes)

    offset = now.utcoffset()
    stroffset = ('-' if offset < timedelta(0) else '+')
    stroffset += format_seconds(abs(offset).seconds)

    # Render template
    return render(request, 'registration/profile.html', {
        'form': form,
        'current_timezone': "{} ({}, UTC{})".format(
            now.tzinfo, now.tzname(), stroffset
        ),
    })


@require_safe
@login_required
def course_detail(request, course_code):
    course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        course__code=course_code,
    )
    course = course_user.course

    return render(request, 'registration/course_detail.html', {
        'course': course,
        'my_course_user': course_user,
        'is_instructor': course_user.user_type == CourseUser.INSTRUCTOR,
    })


@require_safe
@login_required
def course_manage(request, course_code):
    course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        user_type=CourseUser.INSTRUCTOR,
        course__code=course_code,
    )
    course = course_user.course

    return render(request, 'registration/course_manage.html', {
        'course': course,
        'my_course_user': course_user,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_manage_edit(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        user_type=CourseUser.INSTRUCTOR,
        course=course,
    )

    if request.method == 'POST':
        # Populate form with request data
        form = CourseEditForm(request.POST, instance=course)

        # Check for validity
        if form.is_valid():
            course = form.save()
            messages.success(request,
                "The course was updated successfully.",
            )
            return HttpResponseRedirect(reverse(
                'registration:course-manage',
                args=[course.code],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = CourseEditForm(instance=course)

    return render(request, 'registration/course_manage_edit.html', {
        'course': course,
        'my_course_user': course_user,
        'form': form,
    })


@require_safe
@login_required
def course_users(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    my_course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        user_type=CourseUser.INSTRUCTOR,
        course=course,
    )

    return render(request, 'registration/course_users.html', {
        'course': course,
        'my_course_user': my_course_user,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_users_create(request, course_code):
    course = get_object_or_404(Course, code=course_code)
    my_course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        user_type=CourseUser.INSTRUCTOR,
        course=course,
    )

    if request.method == 'POST':
        # Populate form with request data
        form = CourseUserCreateForm(request.POST)

        # Check for validity
        if form.is_valid():
            course_user = form.save(commit=False)
            course_user.course = course
            course_user.save()

            messages.success(request,
                "The course user was updated successfully.",
            )
            return HttpResponseRedirect(reverse(
                'registration:course-users',
                args=[course.code],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = CourseUserCreateForm()

    return render(request, 'registration/course_users_create.html', {
        'course': course,
        'my_course_user': my_course_user,
        'form': form,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_users_edit(request, course_code, course_user_id):
    course = get_object_or_404(Course, code=course_code)
    my_course_user = get_object_or_404(
        CourseUser,
        user=request.user.id,
        user_type=CourseUser.INSTRUCTOR,
        course=course,
    )

    # Find user in question
    course_user = get_object_or_404(
        CourseUser,
        pk=course_user_id,
        course=course,
    )

    if request.method == 'POST':
        # Populate form with request data
        form = CourseUserEditForm(request.POST, instance=course_user)

        # Check for validity
        if form.is_valid():
            course_user = form.save()
            messages.success(request,
                "The course user was updated successfully.",
            )
            return HttpResponseRedirect(reverse(
                'registration:course-users',
                args=[course.code],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = CourseUserEditForm(instance=course_user)

    return render(request, 'registration/course_users_edit.html', {
        'course': course,
        'my_course_user': my_course_user,
        'course_user': course_user,
        'form': form,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def exam_detail(request, course_code, exam_id):
    exam = get_object_or_404(
        Exam,
        pk=exam_id,
        course__code=course_code,
    )
    exam_reg = get_object_or_404(
        ExamRegistration,
        course_user__user=request.user.id,
        exam=exam,
    )

    if request.method == 'POST':
        # Populate form with request data
        form = ExamRegistrationForm(request.POST, instance=exam_reg)

        # Check for validity
        if form.is_valid():
            exam_reg = form.save(commit=False)
            exam_slot = exam_reg.exam_slot
            exam_slot_pk = exam_slot.pk if exam_slot is not None else None

            try:
                ExamRegistration.update_slot(exam_reg.pk, exam_slot_pk)
            except IntegrityError as e:
                messages.error(request,
                    "Error while updating database. Your registration "
                    "was not updated."
                )
            else:
                messages.success(request,
                    "Your exam registration was updated successfully.",
                )
                return HttpResponseRedirect(reverse(
                    'registration:exam-detail',
                    args=[exam.course.code, exam.id],
                ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = ExamRegistrationForm(instance=exam_reg)


    # Reload exam_reg and related items
    exam_reg.refresh_from_db()
    time_slots = exam.time_slot_set.annotate(
        day=TruncDay('start_time'),
    )
    exam_slots = exam.exam_slot_set.annotate(
        day=TruncDay('start_time_slot__start_time'),
    )

    return render(request, 'registration/exam_detail.html', {
        'form': form,
        'exam': exam,
        'exam_reg': exam_reg,
        'time_slots': time_slots,
        'exam_slots': exam_slots,
    })
