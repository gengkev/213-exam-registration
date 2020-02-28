import pytz

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from simple_history.models import HistoricalRecords


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

    class Meta:
        ordering = ('username',)


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
        default=STUDENT,
    )

    # Type of exam slot this user can select
    NORMAL = 'r'
    EXTENDED_TIME = 'e'
    EXAM_SLOT_TYPE = (
        (NORMAL, "Normal"),
        (EXTENDED_TIME, "Extended time"),
    )
    exam_slot_type = models.CharField(
        max_length=1,
        choices=EXAM_SLOT_TYPE,
        default=NORMAL,
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

    def user_type_display(self):
        return dict(CourseUser.USER_TYPE).get(
            self.user_type,
            "Unknown ({})".format(self.user_type),
        )

    def exam_slot_type_display(self):
        return dict(CourseUser.EXAM_SLOT_TYPE).get(
            self.exam_slot_type,
            "Unknown ({})".format(self.exam_slot_type),
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
        ordering = ('user',)


class GithubToken(models.Model):
    course_user = models.OneToOneField(CourseUser,
        on_delete=models.CASCADE,
        related_name='github_token',
    )
    github_login = models.CharField(max_length=64)
    token_type = models.CharField(max_length=32)
    access_token = models.CharField(max_length=64)
    scope = models.CharField(max_length=64, blank=True)
    authorize_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
        )

    def __str__(self):
        return self.github_login


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
        through_fields=('exam', 'course_user'),
    )
    details = models.TextField(blank=True)
    lock_before = models.DateTimeField(null=True, blank=True)
    lock_after = models.DateTimeField(null=True, blank=True)
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
    room = models.ForeignKey(Room,
        on_delete=models.CASCADE,
        related_name='time_slot_set',
        null=True,
        blank=True,
    )
    capacity = models.PositiveIntegerField()
    history = HistoricalRecords()

    def count_num_registered(self):
        """
        Counts the number of users registered for an exam that takes place
        during this slot. The value of this field should not be greater
        than the capacity of this time slot, unless overridden manually.
        """
        q = self.exam_slot_set \
            .aggregate(overlap_count=models.Sum('reg_count'))
        return q['overlap_count']

    def clean(self, *args, **kwargs):
        """Validates consistency of TimeSlot objects."""
        super(TimeSlot, self).clean(*args, **kwargs)

        if not self.start_time:
            raise ValidationError(dict(start_time='No start time provided'))
        if not self.end_time:
            raise ValidationError(dict(end_time='No end time provided'))

        # Ensure end time is not before start time
        if self.start_time > self.end_time:
            raise ValidationError(dict(end_time=(
                "The selected end time is before the selected start time."
            )))

        # Ensure no overlapping time slots
        q = TimeSlot.objects.exclude(pk=self.pk).filter(
            exam=self.exam,
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if q.exists():
            raise ValidationError(dict(start_time=(
                "The selected start and end times overlap with one or "
                "more existing time slots for this exam."
            )))

    def __str__(self):
        tz = timezone.get_current_timezone()
        return "{:%Y-%m-%d %H:%M} ({})".format(
            self.start_time.astimezone(tz),
            self.room if self.room is not None else 'no room'
        )

    def __repr__(self):
        return "<TimeSlot: {} [{}]>".format(
            str(self), str(self.exam),
        )

    class Meta:
        unique_together = (('exam', 'start_time', 'room'),)
        ordering = ['exam', 'start_time', 'room']


class ExamSlot(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='exam_slot_set',
    )
    start_time_slot = models.ForeignKey(TimeSlot,
        on_delete=models.CASCADE,
        related_name='exam_slot',
    )
    time_slots = models.ManyToManyField(TimeSlot,
        related_name='exam_slot_set',
    )
    reg_count = models.PositiveIntegerField(
        default=0,
        editable=False,
    )
    history = HistoricalRecords()

    # Type of exam slot this is
    exam_slot_type = models.CharField(
        max_length=1,
        choices=CourseUser.EXAM_SLOT_TYPE,
        default=CourseUser.NORMAL,
    )

    def exam_slot_type_display(self):
        return dict(CourseUser.EXAM_SLOT_TYPE).get(
            self.exam_slot_type,
            "Unknown ({})".format(self.exam_slot_type),
        )

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

    def get_room(self):
        """Returns the room corresponding to this exam slot."""
        return self.start_time_slot.room

    def update_reg_count(self):
        """Counts the number of users registered for this slot."""
        with transaction.atomic():
            old_reg_count = self.reg_count
            new_reg_count = self.exam_registration_set.count()

            self.reg_count = new_reg_count
            self.save(update_fields=['reg_count'])

        return 'Updated invalid reg count from {} to {}'.format(
                old_reg_count, new_reg_count)

    def count_slots_left(self):
        """Counts the number of remaining slots for this exam slot."""
        return min(
            time_slot.capacity - time_slot.count_num_registered()
            for time_slot in self.time_slots.all()
        )

    def count_capacity(self):
        """Returns the theoretical capacity if there were no registrations."""
        return min(
            time_slot.capacity
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
        tz = timezone.get_current_timezone()
        return "{:%Y-%m-%d %H:%M} \u2013 {:%Y-%m-%d %H:%M} [room={}] [type={}]".format(
            self.get_start_time().astimezone(tz),
            self.get_end_time().astimezone(tz),
            self.start_time_slot.room,
            self.exam_slot_type_display(),
        )

    def __repr__(self):
        return "<ExamSlot: {} [{}]>".format(
            str(self.start_time_slot), str(self.exam),
        )

    class Meta:
        ordering = ['exam', 'start_time_slot', 'exam_slot_type']


class ExamRegistration(models.Model):
    exam = models.ForeignKey(Exam,
        on_delete=models.CASCADE,
        related_name='exam_registration_set',
    )
    course_user = models.ForeignKey(CourseUser,
        on_delete=models.CASCADE,
        related_name='exam_registration_set',
    )
    # This field should ONLY BE CHANGED by the update_slot() function.
    # Otherwise, the database has the potential to become inconsistent.
    exam_slot = models.ForeignKey(ExamSlot,
        on_delete=models.SET_NULL,
        related_name='exam_registration_set',
        null=True,
        blank=True,
    )
    history = HistoricalRecords()

    # Check-in fields
    checkin_room = models.ForeignKey(Room,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    checkin_user = models.ForeignKey(CourseUser,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    checkout_user = models.ForeignKey(CourseUser,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    checkin_notes = models.TextField(blank=True)
    checkin_time = models.DateTimeField(null=True, blank=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    exam_password = models.CharField(max_length=64, blank=True)

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
        unique_together = (('exam', 'course_user'),)
        ordering = ['course_user', 'exam']

    @classmethod
    def update_slot(cls, exam_reg_pk, exam_slot_pk,
            request_time=None, force=False):

        warnings = set()

        # Check some basic facts
        if True:
            exam_reg = ExamRegistration.objects.get(pk=exam_reg_pk)

            # Enforce lock_before and lock_after
            exam = exam_reg.exam
            if request_time is not None:
                if (exam.lock_before is not None and
                        request_time < exam.lock_before):
                    warnings.add("Exam registration is not yet open")

                if (exam.lock_after is not None and
                        request_time >= exam.lock_after):
                    warnings.add("Exam registration has closed")

            # Don't allow dropped users to change.
            if exam_reg.course_user.dropped:
                warnings.add("You have dropped the course")


        # Begin atomic section
        if not warnings:
            with transaction.atomic():
                exam_reg = ExamRegistration.objects.get(pk=exam_reg_pk)

                # Don't allow checked-in users to change.
                if exam_reg.checkin_time:
                    warnings.add(
                        "You have already been checked in for this exam"
                    )

                # Clear exam slot (in transaction)
                # This is so when counting registered in time slots below,
                # we don't include ourselves in the count
                if exam_reg.exam_slot is not None:
                    old_exam_slot = exam_reg.exam_slot
                    old_exam_slot.reg_count -= 1
                    old_exam_slot.save(update_fields=['reg_count'])

                exam_reg.exam_slot = None
                exam_reg.save(update_fields=['exam_slot'])

                # Try to update the slot
                if exam_slot_pk is not None:

                    # Get new exam slot, time slot list
                    exam_slot = ExamSlot.objects.get(pk=exam_slot_pk)

                    # Check that exam slot type is correct
                    if (exam_slot.exam_slot_type !=
                            exam_reg.course_user.exam_slot_type):
                        warnings.add("Wrong exam slot type")

                    # Check that all time slots have seats
                    for time_slot in exam_slot.time_slots.all():
                        if (time_slot.count_num_registered() >=
                                time_slot.capacity):
                            warnings.add("Not enough seats left")

                    # Update the exam registration
                    exam_slot.reg_count += 1
                    exam_slot.save(update_fields=['reg_count'])

                    exam_reg.exam_slot = exam_slot
                    exam_reg.save(update_fields=['exam_slot'])

            if warnings and not force:
                raise IntegrityError('; '.join(warnings))

        return warnings
