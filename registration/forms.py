from django import forms

from .models import User, ExamRegistration, TimeSlot


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'timezone']


class ExamRegistrationForm(forms.ModelForm):
    time_slot = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.RadioSelect,
        empty_label="(Not registered)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter possible time slots by exam
        exam_reg = kwargs['instance']
        self.fields['time_slot'].queryset = \
            TimeSlot.objects.filter(exam=exam_reg.exam)

    class Meta:
        model = ExamRegistration
        fields = ['time_slot']
