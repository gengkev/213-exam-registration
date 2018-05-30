import pytz

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

class User(AbstractUser):
    """
    A class that extends the AbstractUser model in the event that changes
    to the default model need to be made in the future.
    """
    # username: equal to Andrew ID
    # email: <andrew-id>@andrew.cmu.edu
    # password: should never be set

    timezone = models.CharField(
        max_length=32,
        default='America/New_York',
        help_text="Current time zone of the user.",
    )

    def clean(self, *args, **kwargs):
        """Validates custom attributes in the User model."""
        try:
            pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValidationError(dict(timezone="Timezone is invalid."))


class Course(models.Model):
    code = models.CharField(
        max_length=32,
        unique=True,
        help_text="Unique identifier for the course, e.g. 15213-m18.",
    )
    name = models.CharField(
        max_length=200,
        help_text="A human-readable identifier for the course.",
    )
    users = models.ManyToManyField(User,
        through='CourseUser',
        help_text="Accounts enrolled in this course",
    )

    def __str__(self):
        return self.code


class CourseUser(models.Model):
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
    )

    # Type of account in this course
    INSTRUCTOR = 'i'
    STUDENT = 's'
    USER_TYPE = (
        (INSTRUCTOR, "Instructor"),
        (STUDENT, "Student"),
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
        return '{} ({}) [{}]'.format(
            self.user,
            dict(self.USER_TYPE)[self.user_type],
            self.course.code,
        )

    class Meta:
        unique_together = (('user', 'course'),)


# TODO: consider changing to per-exam, or global
class Room(models.Model):
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} [{self.course.code}]"


class Exam(models.Model):
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    registrations = models.ManyToManyField(CourseUser,
        through='ExamRegistration',
    )
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} [{self.course.code}]"


class TimeSlot(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='time_slot_set',
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    rooms = models.ManyToManyField(Room, blank=True)
    capacity = models.PositiveIntegerField()

    def count_registrations(self):
        """
        Counts the number of users registered for an exam that takes place
        during this slot. The value of this field should not be greater
        than the capacity of this time slot, unless overridden manually.
        """
        q = (self.exam_slot_set
                .annotate(reg_count=models.Count('exam_registration_set'))
                .aggregate(overlap_count=models.Sum('reg_count'))
        )
        return q['overlap_count']

    def clean(self, *args, **kwargs):
        """Validates consistency of TimeSlot objects."""
        q = TimeSlot.objects.exclude(pk=self.pk).filter(
            exam=self.exam,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if q.exists():
            raise ValidationError(dict(start_time=(
                "The selected start and end times overlap with one or "
                "more existing time slots for this exam."
            )))
        super(TimeSlot, self).clean(*args, **kwargs)

    def __str__(self):
        return "TimeSlot {} [{}]".format(
            self.start_time.isoformat(timespec='minutes'),
            self.exam,
        )

    class Meta:
        unique_together = (('exam', 'start_time'),)
        ordering = ['exam', 'start_time']


class ExamSlot(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='exam_slot_set',
    )
    start_time_slot = models.OneToOneField(TimeSlot,
        on_delete=models.CASCADE,
        related_name='exam_slot',
    )
    time_slots = models.ManyToManyField(TimeSlot,
        related_name='exam_slot_set',
    )

    def count_registered(self):
        """Counts the number of users registered for this slot."""
        return self.exam_registration_set.count()

    def clean(self, *args, **kwargs):
        """Validates consistency of ExamSlot objects."""
        if self.start_time_slot.exam != self.exam:
            raise ValidationError(dict(start_time_slot=(
                "Selected start time slot does not belong to the "
                "same exam that this exam slot belongs to."
            )))
        super(ExamSlot, self).clean(*args, **kwargs)

    def __str__(self):
        return "ExamSlot [{}]".format(
            self.start_time_slot,
        )

    class Meta:
        ordering = ['exam', 'start_time_slot']


class ExamRegistration(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='exam_registration_set',
    )
    course_user = models.ForeignKey(CourseUser,
        on_delete=models.CASCADE,
        related_name='exam_registration_set',
    )
    exam_slot = models.ForeignKey(ExamSlot,
        on_delete=models.SET_NULL,
        related_name='exam_registration_set',
        null=True,
        blank=True,
    )

    def clean(self, *args, **kwargs):
        """Validates consistency of ExamRegistration objects."""
        if self.exam_slot and self.exam_slot.exam != self.exam:
            raise ValidationError(dict(exam_slot=(
                "Selected exam slot does not belong to the "
                "same exam that this registration belongs to."
            )))
        if self.exam.course != self.course_user.course:
            raise ValidationError(dict(course_user=(
                "Exam and course user do not belong to the same course."
            )))
        super(ExamRegistration, self).clean(*args, **kwargs)

    def __str__(self):
        return f"{self.course_user.user} for {self.exam.name}"

    class Meta:
        unique_together = (('exam', 'course_user'),)
