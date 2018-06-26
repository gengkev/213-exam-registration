import pytz

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    User, Exam, ExamRegistration, ExamSlot, Course, CourseUser
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
                "{}: {}".format(code, pytz.country_names[code]),
                [(tz, tz) for tz in tzlist],
            )
            for (code, tzlist) in pytz.country_timezones.items()
        ]

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
            'user', 'user_type', 'lecture', 'section', 'dropped'
        ]


class CourseUserImportForm(forms.Form):
    roster_file = forms.FileField(
        required=True,
    )


class CourseUserEditForm(forms.ModelForm):
    class Meta:
        model = CourseUser
        fields = [
            'user_type', 'lecture', 'section', 'dropped'
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
            course.course_user_set.all()


class ExamEditForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'details']


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
