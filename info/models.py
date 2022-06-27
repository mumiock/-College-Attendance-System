from django.db import models
import math
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import *
from datetime import *





# Create your models here.


sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

time_slots = (
    ('7:30 - 8:30', '7:30 - 8:30'),
    ('8:30 - 9:30', '8:30 - 9:30'),
    ('9:30 - 10:30', '9:30 - 10:30'),
    ('11:00 - 11:50', '11:00 - 11:50'),
    ('11:50 - 12:40', '11:50 - 12:40'),
    ('12:40 - 1:30', '12:40 - 1:30'),
    ('2:30 - 3:30', '2:30 - 3:30'),
    ('3:30 - 4:30', '3:30 - 4:30'),
    ('4:30 - 5:30', '4:30 - 5:30'),
)

DAYS_OF_WEEK = (
    ('Pazartesi', 'Pazartesi'),
    ('Salı', 'Salı'),
    ('Çarşamba', 'Çarşamba'),
    ('Perşembe', 'Perşembe'),
    ('Cuma', 'Cuma'),
    ('Cumartesi', 'Cumartesi'),
)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, 'student'):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, 'teacher'):
            return True
        return False


class Dept(models.Model):
    id = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    id = models.CharField(primary_key='True', max_length=50)
    name = models.CharField(max_length=50)
    shortname = models.CharField(max_length=50, default='X')

    def __str__(self):
        return self.name


class Class(models.Model):
    # courses = models.ManyToManyField(Course, default=1)
    id = models.CharField(primary_key='True', max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    sem = models.IntegerField()

    class Meta:
        verbose_name_plural = 'classes'

    def __str__(self):
        d = Dept.objects.get(name=self.dept)
        return '%s : %d %s' % (d.name, self.sem, self.section)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, default=1)
    usn = models.CharField(primary_key='True', max_length=100)
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
    dob = models.DateField(default='1998-01-01')

    def _str_(self):
        return '%s : %s' % (self.usn, self.name)

class StudentCards(models.Model):
    usn = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    rf_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return str(self.name)+str(self.lastname)+ ' : ' + str(self.rf_id)



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default='Male')
    dob = models.DateField(default='1980-01-01')

    def __str__(self):
        return self.name

class TeacherCards(models.Model):
    assing_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    rf_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.name)+str(self.lastname)+ ' : ' + str(self.rf_id)

class Assign(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('course', 'class_id', 'teacher'),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Teacher.objects.get(id=self.teacher_id)
        return '%s : %s : %s' % (te.name, cr.shortname, cl)


class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    period = models.CharField(max_length=50, choices=time_slots, default='11:00 - 11:50')
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)





class AttendanceClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    date = models.CharField(default='2018-10-23 11', max_length=13)
    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance'


class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendanceclass = models.ForeignKey(AttendanceClass, on_delete=models.CASCADE, default=1)
    date = models.CharField(default='2018-10-23 11', max_length=100)
    status = models.BooleanField(default='True')

    def __str__(self):
        usn = self.student.usn
        name = self.student.name
        cname = self.course.id
        return '%s : %s : %s : %s: %s' % (usn, name, self.date, cname, self.status)


class AttendanceTotal(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('student', 'course'),)

    @property
    def att_class(self):
        stud = self.student
        cr = Course.objects.get(name=self.course)
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        return att_class

    @property
    def total_class(self):
        stud = self.student
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        return total_class

    @property
    def attendance(self):
        stud = self.student
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        if total_class == 0:
            attendance = 0
        else:
            attendance = round(att_class / total_class * 100, 2)
        return attendance

    @property
    def classes_to_attend(self):
        stud = self.student
        cr = Course.objects.get(name=self.course)
        total_class = Attendance.objects.filter(course=cr, student=stud).count()
        att_class = Attendance.objects.filter(course=cr, student=stud, status='True').count()
        cta = math.ceil((0.70 * total_class - att_class) / 0.30)
        if cta < 0:
            return 0
        return cta
    
    def __str__(self):
        return '%s : %s : %s : %s' % (self.student.usn, self.student.name, self.course.name, self.attendance)
    


class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        name=self.student.name
        usn=self.student.usn
        course=self.course.id
        course_name = self.course.name
        return '%s : %s : %s : %s ' % (usn, name, course, course_name)
    
    def get_attendance(self):
        a = AttendanceTotal.objects.get(student=self.student, course=self.course)
        return a.attendance


class AttendanceRange(models.Model):
    range_classid = models.CharField(max_length=30)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100 )

class Log(models.Model):
    card_id = models.CharField(max_length=100)
    time_in = models.CharField(max_length=100)
    status_at = models.BooleanField(default='True')
    invalid_entry = models.BooleanField(default='True')
    face_data = models.CharField(max_length=250000) 

    def __str__(self):
        return str(self.card_id) + ' : ' + str(self.time_in)





# Django signals


def daterange(start_date, end_date):
    int_time=int(((end_date - start_date).days)/7)
    rng = range(int_time)
    for n in rng:
        yield start_date + timedelta(days=n*7)


days = {
    'Pazartesi': 1,
    'Salı': 2,
    'Çarşamba': 3,
    'Perşembe': 4,
    'Cuma': 5,
    'Cumartesi': 6,
}


def create_attendance(sender, instance, **kwargs):
    if kwargs['created']:
        start_date = AttendanceRange.objects.all()[:1].get().start_date
        start_date = start_date[:13]

        end_date = AttendanceRange.objects.all()[:1].get().end_date
        end_date = end_date[:13]

        s = datetime.strptime(start_date,"%Y-%m-%d %H")
        e = datetime.strptime(end_date,"%Y-%m-%d %H")
        
        # bu kısımı Daha sonra logtaki time in ile netegre etmek için di çok gerekli değil artık.
        # l_time = Log.objects.order_by('-id').all()[:1].get().time_in
        # log_t = l_time[:10]
        # l = datetime.strptime(log_t,"%Y-%m-%d")

        
        for single_date in daterange(s, e):
            try:
                AttendanceClass.objects.get(date=str(single_date)[:13], assign=instance.assign)
            except AttendanceClass.DoesNotExist:
                a = AttendanceClass(date=str(single_date)[:13], assign=instance.assign)
                a.save()




# def insert_attendance(sender, instance, **kwargs):
#     if kwargs['created']:
#         start_date = AttendanceRange.objects.all()[:1].get().start_date
#         end_date = AttendanceRange.objects.all()[:1].get().end_date
#         log_time= Log.objects.order_by('-id').all()[:1].get().time_in
#         RF_id= Log.objects.order_by('-id').all()[:1].get().card_id
#         master_rfid=TeacherCards.objects.get(rf_id=RF_id).rf_id
#         class_id = AttendanceClass.objects.get(date=log_time[0:10]).id 
#         assc = AttendanceClass.objects.get(id=class_id)
#         ass = assc.assign
#         cr = ass.course
#         cl = ass.class_id
    

#         if start_date <= log_time and log_time <= end_date:

#             info_faceCheck= Log.objects.order_by('-id').all()[:1].get().status_at # DB deki status durumu face_recognition
         

#             if RF_id == master_rfid: # eğer bilgiler doğru sie yoklama açıp tüm sınıfı yok yazan kısım.
#                 if info_faceCheck == True:
#                     for i, s in enumerate(cl.student_set.all()):
#                         status = 0
                        
#                         if assc.status == 1:
#                             try:
#                                 a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
#                                 a.status = status
#                                 a.save()
#                             except Attendance.DoesNotExist:
#                                 a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
#                                 a.save()
#                         else:
#                             a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
#                             a.save()
#                             assc.status = 1
#                             assc.save()
                

#             elif RF_id != master_rfid: # Öğreciyi var yazan kısım.
#                 stud = StudentCards.objects.get(rf_id=RF_id).usn_id
   
#                 if info_faceCheck == True:
#                     cur_stud = cl.student_set.get(usn=stud)
#                     a = Attendance.objects.get(course=cr, student=cur_stud, date=assc.date, attendanceclass=assc)
#                     a.status = True
#                     a.save()

                
            
#         elif end_date <  log_time or log_time < start_date:
#             print('+++++++++++++++ İndex is not inside course period!!! +++++++++++++++++++')


post_save.connect(create_attendance, sender=AssignTime)
# post_save.connect(insert_attendance, sender=Log)

