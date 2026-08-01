from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from accounts.models import User
from departments.models import Department
from doctors.models import DoctorProfile, Availability
from patients.models import PatientProfile
from appointments.models import Appointment
from medical_history.models import MedicalHistory


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Departments
        departments_data = [
            ('Cardiology', 'Heart and cardiovascular system care', 'bi-heart-pulse'),
            ('Dermatology', 'Skin, hair, and nails treatment', 'bi-droplet'),
            ('Neurology', 'Brain and nervous system specialists', 'bi-lightbulb'),
            ('Orthopedics', 'Bone and joint care', 'bi-person-arms-up'),
            ('Pediatrics', 'Child healthcare', 'bi-emoji-smile'),
            ('Gynecology', 'Women\'s reproductive health', 'bi-gender-female'),
            ('General Medicine', 'General health consultations', 'bi-hospital'),
            ('Dentistry', 'Dental and oral health', 'bi-emoji-laughing'),
        ]
        depts = {}
        for name, desc, icon in departments_data:
            d, _ = Department.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
            depts[name] = d
        self.stdout.write(self.style.SUCCESS(f'  {len(depts)} departments'))

        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@mediconnect.com', password='admin123',
                first_name='System', last_name='Admin', role='admin', is_approved=True
            )
            self.stdout.write(self.style.SUCCESS('  Admin created: admin / admin123'))

        # Doctors
        doctors_data = [
            ('doctor1', 'Alice', 'Rahman', 'Cardiology', 'MBBS, MD (Cardio)', 'Interventional Cardiology', 12, 800),
            ('doctor2', 'Bob', 'Karim', 'Dermatology', 'MBBS, DDV', 'Cosmetic Dermatology', 8, 600),
            ('doctor3', 'Carol', 'Islam', 'Neurology', 'MBBS, FCPS (Neuro)', 'Stroke Management', 15, 1000),
            ('doctor4', 'David', 'Hasan', 'Orthopedics', 'MBBS, MS (Ortho)', 'Joint Replacement', 10, 900),
            ('doctor5', 'Eva', 'Chowdhury', 'Pediatrics', 'MBBS, DCH', 'Newborn Care', 7, 500),
        ]
        for username, fn, ln, dept_name, qual, spec, exp, fee in doctors_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, email=f'{username}@mediconnect.com',
                    password='doctor123', first_name=fn, last_name=ln,
                    role='doctor', is_approved=True, phone='01700000000'
                )
                DoctorProfile.objects.create(
                    user=user, department=depts[dept_name],
                    specialization=spec, qualification=qual,
                    experience_years=exp, consultation_fee=fee,
                    bio=f'Experienced {dept_name} specialist with {exp} years of practice.'
                )
                # Add sample availability
                for day in ['MON', 'WED', 'FRI']:
                    Availability.objects.get_or_create(
                        doctor=user.doctor_profile, day=day,
                        start_time=time(10, 0), end_time=time(13, 0)
                    )
        self.stdout.write(self.style.SUCCESS('  5 doctors created (username: doctor1..5, password: doctor123)'))

        # Pending doctor (for admin to approve demo)
        if not User.objects.filter(username='doctor_pending').exists():
            u = User.objects.create_user(
                username='doctor_pending', email='pending@mediconnect.com',
                password='doctor123', first_name='Pending', last_name='Doctor',
                role='doctor', is_approved=False
            )
            DoctorProfile.objects.create(
                user=u, department=depts['General Medicine'],
                specialization='General Practice', qualification='MBBS',
                experience_years=3, consultation_fee=400
            )

        # Patients
        patients_data = [
            ('patient1', 'John', 'Ahmed', 28, 'M', 'A+'),
            ('patient2', 'Sara', 'Khan', 24, 'F', 'B+'),
            ('patient3', 'Mike', 'Rahman', 35, 'M', 'O+'),
        ]
        for username, fn, ln, age, gender, bg in patients_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, email=f'{username}@mediconnect.com',
                    password='patient123', first_name=fn, last_name=ln,
                    role='patient', is_approved=True, phone='01800000000'
                )
                PatientProfile.objects.create(
                    user=user, age=age, gender=gender, blood_group=bg,
                    address='Dhaka, Bangladesh'
                )
        self.stdout.write(self.style.SUCCESS('  3 patients created (username: patient1..3, password: patient123)'))

        # Sample appointments
        p1 = PatientProfile.objects.get(user__username='patient1')
        d1 = DoctorProfile.objects.get(user__username='doctor1')
        d2 = DoctorProfile.objects.get(user__username='doctor2')

        Appointment.objects.get_or_create(
            patient=p1, doctor=d1,
            appointment_date=timezone.localdate() + timedelta(days=2),
            appointment_time=time(11, 0),
            defaults={'reason': 'Chest pain and shortness of breath', 'status': 'pending'}
        )
        Appointment.objects.get_or_create(
            patient=p1, doctor=d2,
            appointment_date=timezone.localdate() - timedelta(days=3),
            appointment_time=time(11, 0),
            defaults={'reason': 'Skin rash on arms', 'status': 'completed'}
        )
        self.stdout.write(self.style.SUCCESS('  Sample appointments created'))

        # Medical history
        MedicalHistory.objects.get_or_create(
            patient=p1, condition='Hypertension',
            diagnosed_date=timezone.localdate() - timedelta(days=365),
            defaults={'notes': 'Under medication'}
        )

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:   admin / admin123')
        self.stdout.write('  Doctor:  doctor1 / doctor123')
        self.stdout.write('  Patient: patient1 / patient123')
