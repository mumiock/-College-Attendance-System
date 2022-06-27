from datetime import *
from info.models import *
import time




def insert_attendance():
    
    start_date = AttendanceRange.objects.all()[:1].get().start_date
    end_date = AttendanceRange.objects.all()[:1].get().end_date
    log_time= Log.objects.order_by('-id').all()[:1].get().time_in
    RF_id= Log.objects.order_by('-id').all()[:1].get().card_id
    
    try:
        class_id = AttendanceClass.objects.get(date=log_time[:13]).id 
    except AttendanceClass.DoesNotExist:
        return 'Hata' 

    assc = AttendanceClass.objects.get(id=class_id)
    ass = assc.assign
    cr = ass.course
    cl = ass.class_id

    if start_date <= log_time and log_time <= end_date:

        info_faceCheck= Log.objects.order_by('-id').all()[:1].get().status_at # DB deki status durumu face_recognition
        try:
            master_rfid=TeacherCards.objects.get(rf_id=RF_id).rf_id
        except TeacherCards.DoesNotExist:
            master_rfid=''
            print('Skip!!')    

        if RF_id == master_rfid: # eğer bilgiler doğru sie yoklama açıp tüm sınıfı yok yazan kısım.
            if info_faceCheck == True:
                for i, s in enumerate(cl.student_set.all()):
                    status = 0
                        
                    if assc.status == 1:
                        try:
                            a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
                            a.status = status
                            a.save()
                        except Attendance.DoesNotExist:
                            a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                            a.save()
                    else:
                        a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                        a.save()
                        assc.status = 1
                        assc.save()
                

        elif RF_id != master_rfid: # Öğreciyi var yazan kısım.
   
            if info_faceCheck == True:
                
                try:
                    stud = StudentCards.objects.get(rf_id=RF_id).usn_id
                    cur_stud = cl.student_set.get(usn=stud)
                    a = Attendance.objects.get(course=cr, student=cur_stud, date=assc.date, attendanceclass=assc)
                    a.status = True
                    a.save()
                except Attendance.DoesNotExist or StudentCards.DoesNotExist:
                    print('skip!')    

                
            
    elif end_date <  log_time or log_time < start_date:
        print('+++++++++++++++ İndex is not inside course period!!! +++++++++++++++++++')


def at_func(input):
    if input==True:
        hold=1
        while True:

            time.sleep(2)

            db_id = Log.objects.order_by('-id').all()[:1].get().id
            
            print(hold)

            if db_id!=hold:    
                hold=db_id
                insert_attendance()
            else:
                hold=db_id  
