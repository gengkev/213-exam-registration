import pytz

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from simple_history.models import HistoricalRecords

from examreg import settings


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
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        """Validates custom attributes in the User model."""
        try:
            pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValidationError(dict(timezone="Timezone is invalid."))

    def configure_new(self):
        """
        Configures a newly created user after creation by updating email
        address and password fields accordingly.
        """
        self.email = self.username + settings.ANDREW_EMAIL_SUFFIX
        self.set_unusable_password()
        self.save()

        # TODO: use info from CMU LDAP.
        # https://github.com/ScottyLabs/directory-api/blob/master/server.js



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
    history = HistoricalRecords()

    def __str__(self):
        return self.code


class CourseUser(models.Model):
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
        related_name='course_user_set',
    )
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
        related_name='course_user_set',
    )
    history = HistoricalRecords()

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
    lecture = models.CharField(
        max_length=32,
        blank=True,
        help_text="The student's lecture number",
    )
    section = models.CharField(
        max_length=32,
        blank=True,
        help_text="The student's section number",
    )
    dropped = models.BooleanField(
        default=False,
        help_text=(
            "Whether the student has dropped this course. This prevents "
            "the student from updating any information related to this "
            "course, although they can continue to log in."
        ),
    )

    def is_instructor(self):
        """Returns whether this course user is an instructor."""
        return self.user_type == CourseUser.INSTRUCTOR

    def __str__(self):
        return '{} [{}]'.format(
            self.user,
            self.course.code,
        )

    class Meta:
        unique_together = (('user', 'course'),)
        ordering = ('user__username',)


# TODO: consider changing to per-exam, or global
class Room(models.Model):
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Room: {} [{}]>".format(
            self.name, self.course.code,
        )


class Exam(models.Model):
    course = models.ForeignKey(Course,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=200)
    registrations = models.ManyToManyField(CourseUser,
        through='ExamRegistration',
    )
    details = models.TextField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Exam: {} [{}]>".format(
            self.name, self.course.code,
        )


class TimeSlot(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='time_slot_set',
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    rooms = models.ManyToManyField(Room, blank=True)
    capacity = models.PositiveIntegerField()
    history = HistoricalRecords()

    def count_num_registered(self):
        """
        Counts the number of users registered for an exam that takes place
        during this slot. The value of this field should not be greater
        than the capacity of this time slot, unless overridden manually.
        """
        q = self.exam_slot_set \
            .annotate(reg_count=models.Count('exam_registration_set')) \
            .aggregate(overlap_count=models.Sum('reg_count'))
        return q['overlap_count']

    def clean(self, *args, **kwargs):
        """Validates consistency of TimeSlot objects."""

        # Ensure end time is not before start time
        if self.start_time > self.end_time:
            raise ValidationError(dict(end_time=(
                "The selected end time is before the selected start time."
            )))

        # Ensure no overlapping time slots
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
        return "{:%Y-%m-%d %H:%M}".format(self.start_time)

    def __repr__(self):
        return "<TimeSlot: {} [{}]>".format(
            str(self), str(self.exam),
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
    history = HistoricalRecords()

    def get_start_time(self):
        """Returns the start time of this exam slot."""
        return self.start_time_slot.start_time

    def get_end_time(self):
        """Returns the end time of this exam slot."""
        q = self.time_slots \
            .order_by('-end_time') \
            .values('end_time') \
            .first()
        return q['end_time']

    def count_num_registered(self):
        """Counts the number of users registered for this slot."""
        return self.exam_registration_set.count()

    def count_slots_left(self):
        """Counts the number of remaining slots for this exam slot."""
        return min(
            time_slot.capacity - time_slot.count_num_registered()
            for time_slot in self.time_slots.all()
        )

    def clean(self, *args, **kwargs):
        """Validates consistency of ExamSlot objects.

        Note that we can't test whether each of the TimeSlot objects in
        time_slots belong to the correct exam, because Django doesn't let us
        access those fields before saving. So forms must restrict this
        separately.
        """
        if self.start_time_slot.exam != self.exam:
            raise ValidationError(dict(start_time_slot=(
                "Selected start time slot does not belong to the "
                "same exam that this exam slot belongs to."
            )))
        super(ExamSlot, self).clean(*args, **kwargs)

    def __str__(self):
        return "{:%Y-%m-%d %H:%M} \u2013 {:%Y-%m-%d %H:%M}".format(
            self.get_start_time(),
            self.get_end_time(),
        )

    def __repr__(self):
        return "<ExamSlot: {} [{}]>".format(
            str(self.start_time_slot), str(self.exam),
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
    history = HistoricalRecords()

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
        return "{} for {}".format(
            self.course_user.user,
            self.exam.name,
        )

    class Meta:
        ordering = ['course_user__user__username']
        unique_together = (('exam', 'course_user'),)

    @classmethod
    def update_slot(cls, exam_reg_pk, exam_slot_pk):
        with transaction.atomic():
            exam_reg = ExamRegistration.objects \
                .select_for_update() \
                .get(pk=exam_reg_pk)

            # Clear exam slot (in transaction)
            # This is so when counting registered in time slots below,
            # we don't include ourselves in the count
            exam_reg.exam_slot = None
            exam_reg.save(update_fields=['exam_slot'])

            # Try to update the slot
            if exam_slot_pk is not None:

                # Get new exam slot, time slot list
                exam_slot = ExamSlot.objects \
                    .get(pk=exam_slot_pk)
                time_slot_list = exam_slot.time_slots \
                    .select_for_update()

                # Check that all time slots have seats
                for time_slot in time_slot_list:
                    if (time_slot.count_num_registered() >=
                            time_slot.capacity):
                        raise IntegrityError("Not enough seats left")

                # Update the exam registration
                exam_reg.exam_slot = exam_slot
                exam_reg.save(update_fields=['exam_slot'])
