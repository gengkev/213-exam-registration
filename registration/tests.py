from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import User, Course, CourseUser


class UserModelTests(TestCase):

    def test_clean_rejects_invalid_timezones(self):
        """
        clean() rejects an invalid value for the `timezone` field
        that pytz does not recognize.
        """
        timezone = 'America/Pittsburgh'
        user = User(timezone=timezone)
        with self.assertRaises(ValidationError):
            user.clean()

    def test_clean_accepts_valid_timezones(self):
        """
        clean() accepts a valid value for the `timezone` field
        that pytz recognizes.
        """
        timezone = 'America/New_York'
        user = User(timezone=timezone)
        user.clean()


class LoginTests(TestCase):
    def test_not_logged_in(self):
        """
        If the user is not logged in, then they are redirected to the
        login page.
        """
        response = self.client.get('/',
            follow=True,
        )
        self.assertRedirects(response, '/accounts/login/?next=/')
        self.assertContains(response,
            "your session is not associated with an identity")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_invalid_user_login(self):
        """
        If the user is logged in with an invalid identity, then they
        are redirected to the login page.
        """
        response = self.client.get('/',
            follow=True,
            REMOTE_USER='baduser@cs.cmu.edu',
        )
        self.assertRedirects(response, '/accounts/login/?next=/')
        self.assertContains(response,
            "your current identity provided by the authentication server")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_existing_user_login(self):
        """
        If a valid user who already exists in the database tries to
        log in, then they are logged in correctly.
        """
        user = User.objects.create(username='tester')
        response = self.client.get('/',
            REMOTE_USER='tester@andrew.cmu.edu',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)

    def test_new_user_login(self):
        """
        If a valid user who isn't currently in the database tries to
        log in, then they are immediately logged in and a database
        entry is created for them.
        """
        response = self.client.get('/',
            REMOTE_USER='newuser@andrew.cmu.edu',
        )
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='newuser')
        self.assertEqual(response.context['user'], user)


class IndexViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='tester')
        self.client.defaults['REMOTE_USER'] = 'tester@andrew.cmu.edu'

        course1 = Course.objects.create(
            code='15101-m18',
            name='Introduction to Computer Systems (Summer 2018)',
        )
        course2 = Course.objects.create(
            code='15123-s18',
            name='Principles of Functional Programming (Spring 2018)',
        )

    def test_no_enrolled_courses(self):
        """
        If the user isn't enrolled in any courses, an appropriate
        message is displayed.
        """
        response = self.client.get(reverse('registration:index'))
        self.assertEqual(response.status_code, 200)

        # Check response queryset
        self.assertQuerysetEqual(
            response.context['course_user_list'],
            []
        )

        # Check response body
        self.assertContains(response,
            "You are not enrolled in any courses.")
        self.assertNotContains(response,
            "Principles of Functional Programming (Spring 2018)")
        self.assertNotContains(response,
            "Introduction to Computer Systems (Summer 2018)")

    def test_student_courses(self):
        """
        If the user is enrolled as a student in multiple courses,
        both of them should be listed on the home page.
        """
        course_user_1 = CourseUser.objects.create(
            user=User.objects.get(username='tester'),
            course=Course.objects.get(code='15101-m18'),
            user_type=CourseUser.STUDENT,
            dropped=False,
        )
        course_user_2 = CourseUser.objects.create(
            user=User.objects.get(username='tester'),
            course=Course.objects.get(code='15123-s18'),
            user_type=CourseUser.STUDENT,
            dropped=False,
        )

        response = self.client.get(reverse('registration:index'))
        self.assertEqual(response.status_code, 200)

        # Check response queryset
        self.assertQuerysetEqual(
            response.context['course_user_list'],
            [
                '<CourseUser: tester (Student) [15101-m18]>',
                '<CourseUser: tester (Student) [15123-s18]>',
            ],
            ordered=False,
        )

        # Check response body
        self.assertNotContains(response,
            "You are not enrolled in any courses.")
        self.assertContains(response,
            "Principles of Functional Programming (Spring 2018)")
        self.assertContains(response,
            "Introduction to Computer Systems (Summer 2018)")

