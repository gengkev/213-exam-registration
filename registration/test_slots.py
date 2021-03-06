import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import dateparse

from .models import (
    User, Course, CourseUser, Exam, TimeSlot, ExamSlot, ExamRegistration,
)


def make_exam(self):
    # Create course / exam
    self.course = Course.objects.create(
        code='15101-m18',
        name="Introduction to Computer Systems (Summer 2018)",
    )
    self.exam = Exam.objects.create(
        course=self.course,
        name="Final Exam",
    )


def make_time_slots(self):
    # Create times
    self.times = [
        dateparse.parse_datetime('2018-07-04T17:00Z'),
        dateparse.parse_datetime('2018-07-04T18:00Z'),
        dateparse.parse_datetime('2018-07-04T19:00Z'),
        dateparse.parse_datetime('2018-07-04T20:00Z'),
    ]

    # Create time slots
    self.time_slots = [
        TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[0],
            end_time=self.times[1],
        ),
        TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[1],
            end_time=self.times[2],
        ),
        TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[2],
            end_time=self.times[3],
        ),
    ]


def make_exam_slots(self):
    # Create exam slots
    self.exam_slots = [
        ExamSlot.objects.create(
            exam=self.exam,
            start_time_slot=time_slot,
        )
        for time_slot in self.time_slots
    ]

    # Set time slots on exam slots
    self.exam_slots[0].time_slots.add(self.time_slots[0])
    self.exam_slots[0].time_slots.add(self.time_slots[1])
    self.exam_slots[1].time_slots.add(self.time_slots[1])
    self.exam_slots[1].time_slots.add(self.time_slots[2])
    self.exam_slots[2].time_slots.add(self.time_slots[2])


def make_registered_users(self):
    # Create some users
    self.users = [
        User.objects.create(username='aaa'),
        User.objects.create(username='bbb'),
        User.objects.create(username='ccc'),
    ]

    # Enroll the users in the course
    self.course_users = [
        CourseUser.objects.create(
            user=user,
            course=self.course,
            user_type=CourseUser.STUDENT,
        )
        for user in self.users
    ]

    # Register the users for the exam
    self.exam_registrations = [
        ExamRegistration.objects.create(
            exam=self.exam,
            course_user=course_user,
        )
        for course_user in self.course_users
    ]


class TimeSlotModelTests(TestCase):
    def setUp(self):
        make_exam(self)
        make_time_slots(self)

    def test_db_rejects_duplicate_start_time(self):
        """
        Checks that within the same exam, a time slot with a duplicate
        start time is disallowed by a database constraint.
        """
        with self.assertRaises(IntegrityError):
            new_time_slot = TimeSlot.objects.create(
                exam=self.exam,
                capacity=2,
                start_time=self.times[0],
                end_time=self.times[0] + datetime.timedelta(minutes=30),
            )

    def test_clean_rejects_overlapping_time_slot(self):
        """
        Checks that within the same exam, partially overlapping time
        slots are disallowed by the clean() method.
        """
        new_time_slot = TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[0] - datetime.timedelta(minutes=30),
            end_time=self.times[0] + datetime.timedelta(minutes=1),
        )
        with self.assertRaises(ValidationError):
            new_time_slot.clean()

    def test_clean_rejects_containing_time_slot(self):
        """
        Checks that within the same exam, a time slot that completely
        contain another is disallowed by the clean() method.
        """
        new_time_slot = TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[0] - datetime.timedelta(minutes=30),
            end_time=self.times[3] + datetime.timedelta(minutes=30),
        )
        with self.assertRaises(ValidationError):
            new_time_slot.clean()

    def test_clean_rejects_end_time_before_start_time(self):
        """
        Checks that the end time of a time slot cannot be before the
        start time of that time slot.
        """
        new_time_slot = TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[0] - datetime.timedelta(minutes=30),
            end_time=self.times[0] - datetime.timedelta(minutes=60),
        )
        with self.assertRaises(ValidationError):
            new_time_slot.clean()

    def test_clean_allows_simple_time_slots(self):
        """
        Checks that simple valid time slots, such as the ones made
        for this test, are allowed by the clean() method.
        """
        for time_slot in self.time_slots:
            time_slot.clean()

    def test_clean_allows_same_start_and_end_times(self):
        """
        Checks that if a time slot has the same start and end times, then
        it is allowed by clean().
        """
        new_time_slot = TimeSlot.objects.create(
            exam=self.exam,
            capacity=2,
            start_time=self.times[3],
            end_time=self.times[3],
        )
        new_time_slot.clean()

    def test_clean_allows_overlapping_time_slots_in_different_exams(self):
        """
        Checks that overlapping time slots are allowed by the clean()
        method if they are in different exams.
        """
        new_exam = Exam.objects.create(
            course=self.course,
            name="Midterm Exam",
        )
        new_time_slot = TimeSlot.objects.create(
            exam=new_exam,
            capacity=2,
            start_time=self.times[0],
            end_time=self.times[2] + datetime.timedelta(minutes=30),
        )
        new_time_slot.clean()


class ExamSlotModelTests(TestCase):
    def setUp(self):
        make_exam(self)
        make_time_slots(self)
        make_exam_slots(self)

    def test_start_time_is_correct(self):
        """
        Checks that the get_start_time() method on an ExamSlot returns
        the correct result.
        """
        for exam_slot, start_time in zip(self.exam_slots, self.times):
            self.assertEqual(exam_slot.get_start_time(), start_time)

    def test_end_time_is_correct(self):
        """
        Checks that the get_end_time() method on an ExamSlot returns the
        correct result.
        """
        end_times = [self.times[2], self.times[3], self.times[3]]
        for exam_slot, end_time in zip(self.exam_slots, end_times):
            self.assertEqual(exam_slot.get_end_time(), end_time)

    def test_clean_allows_simple_exam_slots(self):
        """
        Checks that simple valid exam slots, such as the ones made
        for this test, are allowed by the clean() method.
        """
        for exam_slot in self.exam_slots:
            exam_slot.clean()

    def test_clean_rejects_exam_slot_with_different_exam(self):
        """
        Checks that an exam slot whose exam differs from the exam of its
        start_time_slot is rejected by the clean() method.
        """
        new_exam = Exam.objects.create(
            course=self.course,
            name="Midterm Exam",
        )
        self.exam_slots[0].exam = new_exam

        with self.assertRaises(ValidationError):
            self.exam_slots[0].clean()

    def test_db_rejects_duplicate_exam_slots(self):
        """
        Checks that a TimeSlot that is associated with more than one
        ExamSlot via the start_time_slot field is disallowed by a database
        constraint.
        """
        with self.assertRaises(IntegrityError):
            new_exam_slot = ExamSlot.objects.create(
                exam=self.exam,
                start_time_slot=self.time_slots[0],
            )


class ExamRegistrationModelTests(TestCase):
    def setUp(self):
        make_exam(self)
        make_time_slots(self)
        make_exam_slots(self)
        make_registered_users(self)

    def test_clean_allows_empty_exam_slot(self):
        """
        Checks that the clean() method accepts an empty exam slot.
        """
        for exam_reg in self.exam_registrations:
            exam_reg.clean()

    def test_clean_rejects_exam_slot_with_different_exam(self):
        """
        Checks that the clean() method rejects an ExamRegistration whose
        exam_slot is not from the same Exam that the registration is from.
        """
        new_exam = Exam.objects.create(
            course=self.course,
            name="Midterm Exam",
        )
        self.exam_registrations[0].exam = new_exam
        self.exam_registrations[0].exam_slot = self.exam_slots[0]

        with self.assertRaises(ValidationError):
            self.exam_registrations[0].clean()

    def test_clean_rejects_course_user_with_different_course(self):
        """
        Checks that the clean() method rejects an ExamRegistration whose
        course_user is not from the same Course that the exam is from.
        """
        new_course = Course.objects.create(
            code='15123-s18',
            name='Principles of Functional Programming (Spring 2018)',
        )
        new_course_user = CourseUser.objects.create(
            user=self.users[0],
            course=new_course,
        )
        self.exam_registrations[0].course_user = new_course_user

        with self.assertRaises(ValidationError):
            self.exam_registrations[0].clean()


class SlotCountingTests(TestCase):
    def setUp(self):
        make_exam(self)
        make_time_slots(self)
        make_exam_slots(self)
        make_registered_users(self)

    def refresh_objects(self):
        for time_slot in self.time_slots:
            time_slot.refresh_from_db()

        for exam_slot in self.exam_slots:
            exam_slot.refresh_from_db()

        for exam_reg in self.exam_registrations:
            exam_reg.refresh_from_db()

    def test_counts_with_no_registrations(self):
        """
        Tests the results of the accessor methods in TimeSlot and ExamSlot
        when there is one registration.
        """
        self.assertEqual(self.time_slots[0].count_num_registered(), 0)
        self.assertEqual(self.time_slots[1].count_num_registered(), 0)
        self.assertEqual(self.time_slots[2].count_num_registered(), 0)

        self.assertEqual(self.exam_slots[0].reg_count, 0)
        self.assertEqual(self.exam_slots[1].reg_count, 0)
        self.assertEqual(self.exam_slots[2].reg_count, 0)

        self.assertEqual(self.exam_slots[0].count_slots_left(), 2)
        self.assertEqual(self.exam_slots[1].count_slots_left(), 2)
        self.assertEqual(self.exam_slots[2].count_slots_left(), 2)

    def test_counts_with_one_registration(self):
        """
        Tests the results of the accessor methods in TimeSlot and ExamSlot
        when there is one registration.
        """
        ExamRegistration.update_slot(
            self.exam_registrations[0].pk,
            self.exam_slots[1].pk,
        )

        self.refresh_objects()

        self.assertEqual(self.time_slots[0].count_num_registered(), 0)
        self.assertEqual(self.time_slots[1].count_num_registered(), 1)
        self.assertEqual(self.time_slots[2].count_num_registered(), 1)

        self.assertEqual(self.exam_slots[0].reg_count, 0)
        self.assertEqual(self.exam_slots[1].reg_count, 1)
        self.assertEqual(self.exam_slots[2].reg_count, 0)

        self.assertEqual(self.exam_slots[0].count_slots_left(), 1)
        self.assertEqual(self.exam_slots[1].count_slots_left(), 1)
        self.assertEqual(self.exam_slots[2].count_slots_left(), 1)

    def test_counts_with_two_same_registrations(self):
        """
        Tests the results of the accessor methods in TimeSlot and ExamSlot
        when there are two registrations in the same exam slot.
        """
        ExamRegistration.update_slot(
            self.exam_registrations[0].pk,
            self.exam_slots[0].pk,
        )
        ExamRegistration.update_slot(
            self.exam_registrations[1].pk,
            self.exam_slots[0].pk,
        )

        self.refresh_objects()

        self.assertEqual(self.time_slots[0].count_num_registered(), 2)
        self.assertEqual(self.time_slots[1].count_num_registered(), 2)
        self.assertEqual(self.time_slots[2].count_num_registered(), 0)

        self.assertEqual(self.exam_slots[0].reg_count, 2)
        self.assertEqual(self.exam_slots[1].reg_count, 0)
        self.assertEqual(self.exam_slots[2].reg_count, 0)

        self.assertEqual(self.exam_slots[0].count_slots_left(), 0)
        self.assertEqual(self.exam_slots[1].count_slots_left(), 0)
        self.assertEqual(self.exam_slots[2].count_slots_left(), 2)

    def test_counts_with_three_different_registrations(self):
        """
        Tests the results of the accessor methods in TimeSlot and ExamSlot
        when there are three registrations in different exam slots.
        """
        ExamRegistration.update_slot(
            self.exam_registrations[0].pk,
            self.exam_slots[0].pk,
        )
        ExamRegistration.update_slot(
            self.exam_registrations[1].pk,
            self.exam_slots[1].pk,
        )
        ExamRegistration.update_slot(
            self.exam_registrations[2].pk,
            self.exam_slots[2].pk,
        )

        self.refresh_objects()

        self.assertEqual(self.time_slots[0].count_num_registered(), 1)
        self.assertEqual(self.time_slots[1].count_num_registered(), 2)
        self.assertEqual(self.time_slots[2].count_num_registered(), 2)

        self.assertEqual(self.exam_slots[0].reg_count, 1)
        self.assertEqual(self.exam_slots[1].reg_count, 1)
        self.assertEqual(self.exam_slots[2].reg_count, 1)

        self.assertEqual(self.exam_slots[0].count_slots_left(), 0)
        self.assertEqual(self.exam_slots[1].count_slots_left(), 0)
        self.assertEqual(self.exam_slots[2].count_slots_left(), 0)
