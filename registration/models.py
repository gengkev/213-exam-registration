from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    A class that extends the AbstractUser model in the event that changes
    to the default model need to be made in the future.
    """
    # username: equal to Andrew ID
    # email: <andrew-id>@andrew.cmu.edu
    # password: should never be set
    pass


class Course(models.Model):
    code = models.CharField(
        max_length=32,
        primary_key=True,
        help_text='Unique identifier for the course, e.g. 15213-m18.',
    )
    name = models.CharField(
        max_length=200,
        help_text='A human-readable identifier for the course.',
    )
    users = models.ManyToManyField(User,
        through='CourseUser',
        help_text='Accounts enrolled in this course',
    )


class CourseUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    # Type of account in this course
    INSTRUCTOR = 'i'
    STUDENT = 's'
    USER_TYPE = (
        (INSTRUCTOR, 'Instructor'),
        (STUDENT, 'Student'),
    )
    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE,
    )

    # Attributes from Autolab export
    lecture = models.CharField(max_length=32, blank=True)
    section = models.CharField(max_length=32, blank=True)
    dropped = models.BooleanField()


class Room(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    registrations = models.ManyToManyField(User,
        through='ExamRegistration',
    )


class TimeSlot(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    rooms = models.ManyToManyField(Room)


class ExamRegistration(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
    )
    room = models.ForeignKey(Room,
        on_delete=models.SET_NULL,
        null=True,
    )
