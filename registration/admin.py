from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, CourseUser, Room, Exam, TimeSlot, \
        ExamRegistration

admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(CourseUser)
admin.site.register(Room)
admin.site.register(Exam)
admin.site.register(TimeSlot)
admin.site.register(ExamRegistration)
