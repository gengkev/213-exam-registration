from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    User, Course, CourseUser, Room, Exam, TimeSlot, ExamSlot,
    ExamRegistration,
)


# Declare forms for use in inlines

class ExamRegistrationsInstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exam_reg = self.instance

        if exam_reg.pk:
            # Filter selectable exams by course
            course_exams = Exam.objects.filter(
                course=exam_reg.course_user.course)
            self.fields['exam'].queryset = course_exams

            # Filter selectable users by course
            course_users = CourseUser.objects.filter(
                course=exam_reg.exam.course)
            self.fields['course_user'].queryset = course_users

            # Filter selectable exam slots by exam
            exam_slots = ExamSlot.objects.filter(exam=exam_reg.exam)
            self.fields['exam_slot'].queryset = exam_slots


class TimeSlotsInstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        time_slot = self.instance

        # TODO: filter if no object (new entries)
        if time_slot.pk:
            # Filter selectable rooms by course
            course_rooms = Room.objects.filter(course=time_slot.exam.course)
            self.fields['rooms'].queryset = course_rooms


class ExamSlotsInstanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exam_slot = self.instance

        if exam_slot.pk:
            # Filter selectable time slots by exam
            exam_timeslots = TimeSlot.objects.filter(exam=exam_slot.exam)
            self.fields['start_time_slot'].queryset = exam_timeslots
            self.fields['time_slots'].queryset = exam_timeslots

        # Make start_time_slot optional
        self.fields['start_time_slot'].required = False

    def clean(self):
        super().clean()

        # Set start_time_slot correctly
        self.cleaned_data['start_time_slot'] = \
            self.cleaned_data['time_slots'] \
                .order_by('start_time') \
                .first()


# Declare inlines for later use

class CourseUsersInstanceInline(admin.TabularInline):
    model = CourseUser
    extra = 0


class ExamsInstanceInline(admin.TabularInline):
    model = Exam
    extra = 0


class ExamRegistrationsInstanceInline(admin.TabularInline):
    model = ExamRegistration
    form = ExamRegistrationsInstanceForm
    extra = 0


class TimeSlotsInstanceInline(admin.TabularInline):
    model = TimeSlot
    form = TimeSlotsInstanceForm
    extra = 0


class ExamSlotsInstanceInline(admin.TabularInline):
    model = ExamSlot
    form = ExamSlotsInstanceForm
    extra = 0


class RoomsInstanceInline(admin.TabularInline):
    model = Room
    extra = 0


# Declare custom admins

@admin.register(User)
class MyUserAdmin(UserAdmin, SimpleHistoryAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Custom options', {
            'fields': ('timezone',),
        }),
    )


@admin.register(Course)
class CourseAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'name')
    inlines = [
        RoomsInstanceInline,
        ExamsInstanceInline,
        CourseUsersInstanceInline,
    ]


@admin.register(CourseUser)
class CourseUserAdmin(SimpleHistoryAdmin):
    list_display = (
        'user', 'course', 'user_type', 'lecture', 'section', 'dropped',
    )
    list_filter = ('course', 'user_type', 'dropped')
    inlines = [
        ExamRegistrationsInstanceInline,
    ]


@admin.register(Exam)
class ExamAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'course')
    list_filter = ('course',)
    inlines = [
        TimeSlotsInstanceInline,
        ExamSlotsInstanceInline,
        ExamRegistrationsInstanceInline,
    ]
