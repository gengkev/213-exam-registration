import codecs
import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.db.models.functions import TruncDay
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse
from django.utils import timezone
from django.views import generic
from django.views.decorators.http import (
    require_http_methods, require_safe, require_POST
)

from examreg import settings

from .forms import (
    ProfileForm, ExamRegistrationForm, CourseEditForm, CourseSudoForm,
    CourseUserEditForm, CourseUserCreateForm, CourseUserImportForm,
    ExamEditForm,
)
from .models import (
    Course, CourseUser, Exam, ExamRegistration, User
)


def course_auth(request, course_code, instructor=False, use_sudo=True):
    """
    Checks whether a user is enrolled in the course. If so, a 2-tuple
    (course, course_user) is returned, and otherwise, a PermissionDenied
    exception is raised. If the course doesn't exist, Http404 is raised.

    If instructor is True, then only instructors are permitted to access
    the course. If use_sudo is True, then the sudo user will be used if
    activated in the session.
    """
    course = get_object_or_404(Course, code=course_code)

    # Try to use sudo
    sudo = request.session.get('sudo_user', None)
    if (use_sudo and sudo is not None and
            sudo['course_code'] == course_code):
        query = {'course': course, 'pk': sudo['pk']}
        request.sudo_enabled = True
    else:
        query = {'course': course, 'user': request.user.id}

    # Limit to instructors if necessary
    if instructor:
        query['user_type'] = CourseUser.INSTRUCTOR

    # Look up CourseUser in database
    try:
        course_user = CourseUser.objects.get(**query)
    except CourseUser.DoesNotExist:
        raise PermissionDenied("You are not enrolled in this course.")

    return course, course_user


@require_safe
@login_required
def index(request):
    """
    Displays the home page, with all courses the user is enrolled in. If
    the user is not authenticated, displays an error message.
    """
    user = get_object_or_404(User, pk=request.user.id)
    course_user_list = user.course_user_set.all()
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
    stroffset = 'UTC{}{}'.format(
        '-' if offset < timedelta(0) else '+',
        format_seconds(abs(offset).seconds),
    )

    # Render template
    return render(request, 'registration/profile.html', {
        'form': form,
        'timezone_name': now.tzinfo,
        'timezone_utc_offset': stroffset,
    })


@require_safe
@login_required
def course_detail(request, course_code):
    course, my_course_user = course_auth(request, course_code)

    # Get list of (exam, exam_reg)
    def get_exam_reg(exam):
        try:
            return ExamRegistration.objects.get(
                exam=exam,
                course_user=my_course_user,
            )
        except ExamRegistration.DoesNotExist:
            return None

    exam_list = [
        (exam, get_exam_reg(exam))
        for exam in course.exam_set.all()
    ]

    return render(request, 'registration/course_detail.html', {
        'course': course,
        'my_course_user': my_course_user,
        'exam_list': exam_list,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_edit(request, course_code):
    course, _ = course_auth(request, course_code, instructor=True)

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
                'registration:course-detail',
                args=[course.code],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = CourseEditForm(instance=course)

    return render(request, 'registration/course_edit.html', {
        'course': course,
        'form': form,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_sudo(request, course_code):
    course, _ = course_auth(request, course_code,
            instructor=True, use_sudo=False)

    # Check for previous sudo user
    prev_sudo_user = None
    if 'sudo_user' in request.session:
        prev_sudo_user = CourseUser.objects.get(
            pk=request.session['sudo_user']['pk'],
        )

    if request.method == 'POST':
        # Populate form with request data
        form = CourseSudoForm(request.POST, course=course)

        # Check for validity
        if form.is_valid():
            new_sudo_user = form.cleaned_data['user']

            if prev_sudo_user is not None:
                messages.warning(request,
                    "You are no longer acting as {}."
                        .format(prev_sudo_user)
                )

            if new_sudo_user is None:
                # Clear sudo user
                del request.session['sudo_user']

            else:
                # Set new sudo user
                request.session['sudo_user'] = {
                    'str': str(new_sudo_user),
                    'pk': new_sudo_user.pk,
                    'user_pk': new_sudo_user.user.pk,
                    'course_code': course.code,
                }
                messages.success(request,
                    "You are now acting as {}."
                        .format(new_sudo_user),
                )

            return HttpResponseRedirect(reverse(
                'registration:course-detail',
                args=[course.code],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = CourseSudoForm(
            course=course,
            initial={'user': prev_sudo_user}
        )

    return render(request, 'registration/course_sudo.html', {
        'course': course,
        'form': form,
    })


@require_safe
@login_required
def course_users(request, course_code):
    course, _ = course_auth(request, course_code, instructor=True)

    return render(request, 'registration/course_users.html', {
        'course': course,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_users_create(request, course_code):
    course, _ = course_auth(request, course_code, instructor=True)

    if request.method == 'POST':
        # Populate form with request data
        form = CourseUserCreateForm(request.POST, course=course)

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
        form = CourseUserCreateForm(course=course)

    return render(request, 'registration/course_users_create.html', {
        'course': course,
        'form': form,
    })


def import_roster_row(course, row):
    """
    Imports a CSV row from a roster. The row should be represented as a
    dictionary, with the columns having been already mapped to the
    appropriate keys by a DictReader. A ValueError will be raised if
    invalid data is encountered, and an IntegrityError may be raised by
    the database (though this is not expected).

    The function will create a User and CourseUser from the row's data.
    When dealing with users that already exists, the current behavior is to
    preserve rather than overwrite any existing data.
    """
    # Parse username
    if 'username' in row and row['username']:
        username = row['username']

    elif 'email' in row and row['email']:
        if not row['email'].endswith(settings.ANDREW_EMAIL_SUFFIX):
            raise ValueError("Invalid email: " + row['email'])
        username = row['email'][:-len(settings.ANDREW_EMAIL_SUFFIX)]

    else:
        raise ValueError("Neither username nor email present in row")

    # Create User, or get if already exists
    extra_keys = ['first_name', 'last_name']
    extra_dict = {k: row[k] for k in extra_keys if k in row and row[k]}

    user, created_user = User.objects.get_or_create(
        username=username,
        defaults=extra_dict,
    )

    if created_user:
        user.configure_new()

    # Create CourseUser, or get if already exists
    extra_keys = ['section', 'lecture']
    extra_dict = {k: row[k] for k in extra_keys if k in row and row[k]}
    extra_dict.update(dict(
        dropped=False,
        user_type=CourseUser.STUDENT,
    ))

    course_user, created = CourseUser.objects.get_or_create(
        user=user,
        course=course,
        defaults=extra_dict,
    )

    return created


def import_roster_rows(course, rows):
    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for row in rows:
            created = import_roster_row(course, row)
            if created:
                created_count += 1
            else:
                skipped_count += 1

    return (created_count, skipped_count)


def import_roster_from_csv_file(course, f):
    """
    Imports an entire course roster from a file. The roster is parsed as
    a CSV file in the Autolab format. The import is processed as a
    transaction for speed, and so that any errors will cause the entire
    import to fail.
    """
    # Column headers for Autolab CSV roster import
    AUTOLAB_FIELDNAMES = [
        'semester', 'email', 'last_name', 'first_name', 'school', 'major',
        'year', 'grading_policy', 'lecture', 'section',
    ]

    with f:
        text_file = codecs.iterdecode(f, 'utf-8')
        reader = csv.DictReader(
            text_file,
            fieldnames=AUTOLAB_FIELDNAMES,
        )
        return import_roster_rows(course, reader)


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_users_import(request, course_code):
    course, _ = course_auth(request, course_code, instructor=True)

    if request.method == 'POST':
        # Populate form with request data
        form = CourseUserImportForm(request.POST, request.FILES)

        # Check for validity
        if form.is_valid():
            try:
                with request.FILES['roster_file'] as f:
                    created_count, skipped_count = \
                        import_roster_from_csv_file(course, f)

            except ValueError as e:
                messages.error(request, (
                    "Failed to import roster: {}"
                ).format(e))

            except IntegrityError as e:
                messages.error(request, (
                    "A database error occurred: {}"
                ).format(e))

            else:
                messages.success(request, (
                    "The roster was imported successfully. {} users "
                    "were created, and {} users were skipped."
                ).format(created_count, skipped_count))

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
        form = CourseUserImportForm()

    return render(request, 'registration/course_users_import.html', {
        'course': course,
        'form': form,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def course_users_edit(request, course_code, course_user_id):
    course, _ = course_auth(request, course_code, instructor=True)

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
        'course_user': course_user,
        'form': form,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def exam_detail(request, course_code, exam_id):
    course, my_course_user = course_auth(request, course_code)
    exam = get_object_or_404(
        Exam,
        pk=exam_id,
        course=course,
    )
    exam_reg, _ = ExamRegistration.objects.get_or_create(
        course_user=my_course_user,
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

    # Determine id of selected slot
    selected_slot = form['exam_slot'].value()
    if selected_slot is not None:
        selected_slot = int(selected_slot)

    return render(request, 'registration/exam_detail.html', {
        'form': form,
        'course': course,
        'my_course_user': my_course_user,
        'exam': exam,
        'exam_reg': exam_reg,
        'time_slots': time_slots,
        'exam_slots': exam_slots,
        'selected_slot': selected_slot,
    })


@require_http_methods(['GET', 'HEAD', 'POST'])
@login_required
def exam_edit(request, course_code, exam_id):
    course, _ = course_auth(request, course_code, instructor=True)
    exam = get_object_or_404(
        Exam,
        pk=exam_id,
        course=course,
    )

    if request.method == 'POST':
        # Populate form with request data
        form = ExamEditForm(request.POST, instance=exam)

        # Check for validity
        if form.is_valid():
            exam = form.save()
            messages.success(request,
                "The exam was updated successfully.",
            )
            return HttpResponseRedirect(reverse(
                'registration:exam-detail',
                args=[course.code, exam.pk],
            ))

        else:
            messages.error(request,
                "Please correct the error below.",
            )

    else:
        # Create default form
        form = ExamEditForm(instance=exam)

    return render(request, 'registration/exam_edit.html', {
        'course': course,
        'exam': exam,
        'form': form,
    })


@require_safe
@login_required
def exam_signups(request, course_code, exam_id):
    course, _ = course_auth(request, course_code, instructor=True)
    exam = get_object_or_404(
        Exam,
        pk=exam_id,
        course=course,
    )

    return render(request, 'registration/exam_signups.html', {
        'course': course,
        'exam': exam,
    })
