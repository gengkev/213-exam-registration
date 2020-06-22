import pytz

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    User, Exam, ExamRegistration, TimeSlot, ExamSlot, Course, CourseUser
)


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hardcode list of CMU timezones
        cmu_timezones = [('CMU Campuses', [
            ('America/New_York', 'Pittsburgh (America/New_York)'),
            ('Asia/Qatar', 'Qatar (Asia/Qatar)'),
            ('America/Los_Angeles', 'Silicon Valley (America/Los_Angeles)'),
        ])]

        # Get timezones by country
        tz_timezones = [
            (
                "{} ({})".format(pytz.country_names[code], code),
                [(tz, tz) for tz in tzlist],
            )
            for (code, tzlist) in pytz.country_timezones.items()
        ]
        tz_timezones.sort()

        # Get all other timezones (ex. UTC)
        other_timezone_set = pytz.common_timezones_set
        for (code, tzlist) in pytz.country_timezones.items():
            other_timezone_set -= set(tzlist)
        other_timezones = [('Other timezones', [
            (tz, tz) for tz in sorted(other_timezone_set)
        ])]

        # Apply to select field
        self.fields['timezone'].widget.choices = (
            cmu_timezones + tz_timezones + other_timezones
        )


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'timezone']
        widgets = {
            'timezone': forms.Select(),
        }


class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code']


class CourseUserCreateForm(forms.ModelForm):
    # Validate Andrew IDs
    user = forms.RegexField(
        required=True,
        strip=True,
        regex=r'^[a-z0-9]{1,30}$',
    )

    def __init__(self, *args, course, **kwargs):
        super().__init__(*args, **kwargs)
        self.course = course

    def clean_user(self):
        """Convert user field into a user object."""
        username = self.cleaned_data['user']
        user, created = User.objects.get_or_create(
            username=username
        )

        if created:
            # Configure newly created user
            user.configure_new()

        else:
            # Check if CourseUser already exists
            try:
                CourseUser.objects.get(course=self.course, user=user)
            except CourseUser.DoesNotExist:
                pass
            else:
                raise ValidationError('Course user already exists.')

        return user

    class Meta:
        model = CourseUser
        fields = [
            'user', 'user_type', 'exam_slot_type', 'lecture',
            'section', 'dropped',
        ]


class CourseUserImportForm(forms.Form):
    roster_file = forms.FileField(
        required=True,
    )


class CourseUserEditForm(forms.ModelForm):
    class Meta:
        model = CourseUser
        fields = [
            'user_type', 'exam_slot_type', 'lecture', 'section', 'dropped'
        ]


class CourseSudoForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=None,
        required=False,
    )

    def __init__(self, *args, course, **kwargs):
        super().__init__(*args, **kwargs)

        # Only select users enrolled in course
        self.fields['user'].queryset = \
            course.course_user_set.select_related('user').all()


class ExamEditForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'details', 'lock_before', 'lock_after']


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time', 'room', 'capacity']


TimeSlotFormSet = forms.inlineformset_factory(
    Exam,
    TimeSlot,
    form=TimeSlotForm,
    extra=0,
)


class ExamSlotForm(forms.ModelForm):
    class Meta:
        model = ExamSlot
        fields = ['time_slots', 'exam_slot_type']


ExamSlotFormSet = forms.inlineformset_factory(
    Exam,
    ExamSlot,
    form=ExamSlotForm,
    extra=0,
)

class ExamRegistrationForm(forms.ModelForm):
    exam_slot = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.RadioSelect,
        to_field_name=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter possible time slots by exam
        exam_reg = self.instance
        self.fields['exam_slot'].queryset = \
            exam_reg.exam.exam_slot_set.all()

    class Meta:
        model = ExamRegistration
        fields = ['exam_slot']


class ExamCheckinForm(forms.ModelForm):
    checkin_room = forms.ModelChoiceField(
        queryset=None,
        required=True,
        empty_label=None,
    )
    checkin_notes = forms.CharField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter possible rooms by course
        exam_reg = self.instance
        course = exam_reg.exam.course
        self.fields['checkin_room'].queryset = course.room_set.all()

    class Meta:
        model = ExamRegistration
        fields = ['checkin_room', 'checkin_notes']


class ExamEditSignupForm(forms.ModelForm):
    checkin_notes = forms.CharField(
        required=False,
    )
    checkin_user = forms.ModelChoiceField(
        queryset=None,
        required=True,
        empty_label=None,
    )
    checkout_user = forms.ModelChoiceField(
        queryset=None,
        required=True,
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter possible check-in users
        exam_reg = self.instance
        course = exam_reg.exam.course
        instructor_set = (course.course_user_set
                .filter(user_type=CourseUser.INSTRUCTOR)
                .select_related('user'))
        self.fields['checkin_user'].queryset = instructor_set
        self.fields['checkout_user'].queryset = instructor_set

    class Meta:
        model = ExamRegistration
        fields = [
            'checkin_room', 'checkin_notes',
            'checkin_user', 'checkin_time',
            'checkout_user', 'checkout_time',
            'exam_password',
        ]
