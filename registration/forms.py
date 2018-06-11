import pytz

from django import forms

from .models import (
    User, ExamRegistration, ExamSlot, Course, CourseUser
)


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Construct list of timezones
        cmu_timezones = [('CMU Campuses', [
            ('America/New_York', 'Pittsburgh (America/New_York)'),
            ('Asia/Qatar', 'Qatar (Asia/Qatar)'),
            ('America/Los_Angeles', 'Silicon Valley (America/Los_Angeles)'),
        ])]

        tz_timezones = [
            (
                "{}: {}".format(code, pytz.country_names[code]),
                [(tz, tz) for tz in tzlist],
            )
            for (code, tzlist) in pytz.country_timezones.items()
        ]

        # Apply to select field
        self.fields['timezone'].widget.choices = (
            cmu_timezones + tz_timezones
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
    class Meta:
        model = CourseUser
        fields = [
            'user', 'user_type', 'lecture', 'section', 'dropped'
        ]


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

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course')
        super().__init__(*args, **kwargs)

        # Only select users enrolled in course
        self.fields['user'].queryset = \
            course.course_user_set.all()


class ExamRegistrationForm(forms.ModelForm):
    exam_slot = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.RadioSelect,
        to_field_name=None,
        empty_label="(Not registered)",
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
