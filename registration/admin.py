from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Course, CourseUser, Room, Exam, TimeSlot, ExamRegistration,
)


# Use default UserAdmin for User
admin.site.register(User, UserAdmin)


# Declare inlines for later use

class CourseUsersInstanceInline(admin.TabularInline):
    model = CourseUser
    extra = 0


class ExamsInstanceInline(admin.TabularInline):
    model = Exam
    extra = 0


class ExamRegistrationsInstanceInline(admin.TabularInline):
    model = ExamRegistration
    extra = 0


class TimeSlotsInstanceInline(admin.TabularInline):
    model = TimeSlot
    extra = 0


class RoomsInstanceInline(admin.TabularInline):
    model = Room
    extra = 0


# Declare custom admins

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    inlines = [
        RoomsInstanceInline,
        ExamsInstanceInline,
        CourseUsersInstanceInline,
    ]


@admin.register(CourseUser)
class CourseUserAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'course', 'user_type', 'lecture', 'section', 'dropped',
    )
    list_filter = ('course', 'user_type', 'dropped')
    inlines = [
        ExamRegistrationsInstanceInline,
    ]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'name')
    list_filter = ('course',)
    inlines = [
        TimeSlotsInstanceInline,
        ExamRegistrationsInstanceInline,
    ]
