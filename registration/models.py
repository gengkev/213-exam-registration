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
        unique=True,
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

    def __str__(self):
        return self.code


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

    def __str__(self):
        return '%s (%s), %s' % (self.user, self.course, self.user_type)

    class Meta:
        unique_together = (('user', 'course'),)


class Room(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return '%s (%s)' % (self.name, self.course)


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    registrations = models.ManyToManyField(CourseUser,
        through='ExamRegistration',
    )

    def __str__(self):
        return '%s (%s)' % (self.name, self.course)


class TimeSlot(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    rooms = models.ManyToManyField(Room)
    capacity = models.PositiveIntegerField()


class ExamRegistration(models.Model):
    # Assume exam.course == user.course
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    course_user = models.ForeignKey(CourseUser, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (('exam', 'course_user'),)
