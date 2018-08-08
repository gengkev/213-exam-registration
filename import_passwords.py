import csv
from registration.models import *

course = Course.objects.get(code='15213-m18')
exam = Exam.objects.get(course=course, name='Final Exam')
print(course, exam)

with open('usernames.txt', newline='') as f:
    r = csv.reader(f)
    for row in r:
        username, password = row
        try:
            course_user = CourseUser.objects.get(
                user__username=username,
                course=course,
            )
        except CourseUser.DoesNotExist:
            print('course user does not exist', username)
        exam_reg, created = ExamRegistration.objects.get_or_create(
            course_user=course_user,
            exam=exam,
        )
        exam_reg.exam_password = password
        exam_reg.save()
