from django.db import models
from django.contrib.auth.models import User

DEPARTMENT_CHOICES = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologist', 'Dermatologist'),
    ('Emergency', 'Emergency'),
    ('Neurologist', 'Neurologist'),
    ('Pediatrician', 'Pediatrician'),
    ('Psychiatrist', 'Psychiatrist'),
]

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    mobile = models.CharField(max_length=20)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Cardiologist')
    address = models.CharField(max_length=100)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    # REMOVED: symptoms field
    admitDate = models.DateField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    @property
    def get_current_doctor(self):
        latest_appointment = Appointment.objects.filter(
            patientId=self, 
            status=True
        ).order_by('-date', '-id').first()
        return latest_appointment.doctorId if latest_appointment else None

class Appointment(models.Model):
    patientId = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctorId = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)  # This is where symptoms go now
    duration = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(auto_now=True)
    status = models.BooleanField(default=False)
    is_discharged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patientId.get_name} - {self.doctorId.get_name if self.doctorId else 'No doctor assigned'}"

class PatientDischargeDetails(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='discharge_details')
    patientId = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctorId = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    admitDate = models.DateField(null=False)
    releaseDate = models.DateField(null=False)
    daySpent = models.PositiveIntegerField(default=0)
    medicineCost = models.PositiveIntegerField(default=0)
    roomCharge = models.PositiveIntegerField(default=0)
    doctorFee = models.PositiveIntegerField(default=0)
    OtherCharge = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.patientId.get_name} - Dr. {self.doctorId.get_name if self.doctorId else 'N/A'} - ${self.total}"