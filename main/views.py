from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from .models import Doctor, Patient, Appointment, PatientDischargeDetails
from .forms import AdminSignupForm, DoctorSignupForm, PatientSignupForm, AppointmentForm, DischargeForm
from .decorators import unauthenticated_user, allowed_users
from .utils import render_to_pdf
from datetime import date, timedelta

# ---- HOME / BASE ----
def home(request):
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# ---- AUTHENTICATION VIEWS ----
@unauthenticated_user
def admin_signup_view(request):
    form = AdminSignupForm()
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            messages.success(request, 'Admin account created! Please login.')
            return redirect('adminlogin')
    return render(request, 'adminsignup.html', {'form': form})

@unauthenticated_user
def doctor_signup_view(request):
    form = DoctorSignupForm()
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            doctor = Doctor(
                user=user,
                mobile=form.cleaned_data['mobile'],
                department=form.cleaned_data['department'],
                address=form.cleaned_data['address'],
                status=False
            )
            doctor.save()
            messages.success(request, 'Doctor registered! Wait for admin approval.')
            return redirect('doctorlogin')
    return render(request, 'doctorsignup.html', {'form': form})

def patient_signup_view(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('home')

    form = PatientSignupForm()
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            patient = Patient(
                user=user,
                mobile=form.cleaned_data['mobile'],
                address=form.cleaned_data['address'],
                # REMOVED: symptoms
                status=True
            )
            patient.save()

            if request.user.is_authenticated and request.user.is_superuser:
                messages.success(request, f'Patient {user.first_name} {user.last_name} created successfully!')
                return redirect('admin-patient')
            else:
                messages.success(request, 'Patient registered! You can login now.')
                return redirect('patientlogin')
        else:
            messages.error(request, 'Please correct the errors below.')
    return render(request, 'patientsignup.html', {'form': form})

@unauthenticated_user
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin.')
    return render(request, 'adminlogin.html')

@unauthenticated_user
def doctor_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                doctor = Doctor.objects.get(user=user)
                if doctor.status:
                    login(request, user)
                    return redirect('doctor-dashboard')
                else:
                    messages.error(request, 'Account not approved by admin yet.')
            except Doctor.DoesNotExist:
                messages.error(request, 'No Doctor profile found.')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'doctorlogin.html')

@unauthenticated_user
def patient_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                patient = Patient.objects.get(user=user)
                if patient.status:
                    login(request, user)
                    return redirect('patient-dashboard')
                else:
                    messages.error(request, 'Account not approved by admin yet.')
            except Patient.DoesNotExist:
                messages.error(request, 'No Patient profile found.')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'patientlogin.html')

# ---- ADMIN VIEWS ----
@allowed_users(allowed_roles=['admin'])
def admin_dashboard_view(request):
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    discharged = PatientDischargeDetails.objects.all()

    context = {
        'total_doctors': doctors.count(),
        'total_patients': patients.count(),
        'pending_doctors': doctors.filter(status=False).count(),
        'pending_appointments': Appointment.objects.filter(status=False).count(),
        'discharged_patients': discharged.count(),
    }
    return render(request, 'admin_dashboard.html', context)

# --- Admin: Doctor Management ---
@allowed_users(allowed_roles=['admin'])
def admin_doctor_view(request):
    doctors = Doctor.objects.all()
    return render(request, 'admin_doctor.html', {'doctors': doctors})

@allowed_users(allowed_roles=['admin'])
def admin_pending_doctor_view(request):
    doctors = Doctor.objects.filter(status=False)
    return render(request, 'admin_pending_doctor.html', {'doctors': doctors})

@allowed_users(allowed_roles=['admin'])
def approve_doctor_view(request, pk):
    doctor = Doctor.objects.get(id=pk)
    doctor.status = True
    doctor.save()
    messages.success(request, f'Dr. {doctor.get_name} has been approved!')
    return redirect('admin-doctor')

@allowed_users(allowed_roles=['admin'])
def delete_doctor_view(request, pk):
    doctor = Doctor.objects.get(id=pk)
    user = User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully!')
    return redirect('admin-doctor')

@allowed_users(allowed_roles=['admin'])
def edit_doctor_view(request, pk):
    doctor = get_object_or_404(Doctor, id=pk)
    user = doctor.user

    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        department = request.POST.get('department')
        address = request.POST.get('address')
        status = request.POST.get('status') == 'on'

        doctor.mobile = mobile
        doctor.department = department
        doctor.address = address
        doctor.status = status
        doctor.save()

        messages.success(request, f'Doctor {user.first_name} {user.last_name} updated successfully!')
        return redirect('admin-doctor')

    context = {
        'doctor': doctor,
        'user': user,
        'departments': [
            ('Cardiologist', 'Cardiologist'),
            ('Dermatologist', 'Dermatologist'),
            ('Emergency', 'Emergency'),
            ('Neurologist', 'Neurologist'),
            ('Pediatrician', 'Pediatrician'),
            ('Psychiatrist', 'Psychiatrist'),
        ]
    }
    return render(request, 'edit_doctor.html', context)

# --- Admin: Patient Management ---
@allowed_users(allowed_roles=['admin'])
def admin_patient_view(request):
    patients = Patient.objects.all()
    return render(request, 'admin_patient.html', {'patients': patients})

@allowed_users(allowed_roles=['admin'])
def admin_unassigned_patient_view(request):
    patients_with_appointments = Appointment.objects.filter(status=True).values_list('patientId_id', flat=True)
    patients = Patient.objects.filter(status=True).exclude(id__in=patients_with_appointments)
    doctors = Doctor.objects.filter(status=True)
    return render(request, 'admin_unassigned_patient.html', {'patients': patients, 'doctors': doctors})

@allowed_users(allowed_roles=['admin'])
def approve_patient_view(request, pk):
    patient = Patient.objects.get(id=pk)
    patient.status = True
    patient.save()
    messages.success(request, f'Patient {patient.get_name} approved!')
    return redirect('admin-patient')

@allowed_users(allowed_roles=['admin'])
def delete_patient_view(request, pk):
    patient = Patient.objects.get(id=pk)
    user = User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    messages.success(request, 'Patient deleted successfully!')
    return redirect('admin-patient')

@allowed_users(allowed_roles=['admin'])
def assign_doctor_view(request, pk):
    if request.method == 'POST':
        patient = Patient.objects.get(id=pk)
        doctor_id = request.POST.get('doctor_id')
        doctor = Doctor.objects.get(id=doctor_id)
        appointment = Appointment(
            patientId=patient,
            doctorId=doctor,
            description='Assigned by admin',
            status=True,
            is_discharged=False
        )
        appointment.save()
        messages.success(request, f'Dr. {doctor.get_name} assigned to {patient.get_name} successfully!')
    return redirect('admin-patient')

# --- Admin: Appointment Management ---
@allowed_users(allowed_roles=['admin'])
def admin_appointment_view(request):
    appointments = Appointment.objects.filter(status=False)
    doctors = Doctor.objects.filter(status=True)
    return render(request, 'admin_appointment.html', {
        'appointments': appointments,
        'doctors': doctors
    })

@allowed_users(allowed_roles=['admin'])
def approve_appointment_view(request, pk):
    if request.method == 'POST':
        appointment = Appointment.objects.get(id=pk)
        doctor_id = request.POST.get('doctor_id')
        if not doctor_id:
            messages.error(request, 'Please select a doctor to assign.')
            return redirect('admin-appointment')

        doctor = Doctor.objects.get(id=doctor_id)
        appointment.doctorId = doctor
        appointment.status = True
        appointment.is_discharged = False
        appointment.save()

        messages.success(request, f'Appointment approved! {appointment.patientId.get_name} assigned to Dr. {doctor.get_name}')
    return redirect('admin-appointment')

@allowed_users(allowed_roles=['admin'])
def reject_appointment_view(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.delete()
    messages.success(request, 'Appointment rejected.')
    return redirect('admin-appointment')

# --- Admin: Discharge ---
@allowed_users(allowed_roles=['admin'])
def admin_discharge_view(request):
    # Get all approved appointments that are NOT discharged
    active_appointments = Appointment.objects.filter(status=True, is_discharged=False)
    discharged = PatientDischargeDetails.objects.all()
    
    return render(request, 'admin_discharge.html', {
        'active_appointments': active_appointments,
        'discharged': discharged
    })

@allowed_users(allowed_roles=['admin'])
def discharge_patient_view(request, pk):
    appointment = get_object_or_404(Appointment, id=pk)
    patient = appointment.patientId
    doctor = appointment.doctorId
    
    if request.method == 'POST':
        form = DischargeForm(request.POST)
        if form.is_valid():
            admit_date = patient.admitDate
            release_date = date.today()
            day_spent = (release_date - admit_date).days
            if day_spent == 0:
                day_spent = 1
            total = form.cleaned_data['medicineCost'] + form.cleaned_data['roomCharge'] + \
                    form.cleaned_data['doctorFee'] + form.cleaned_data['OtherCharge']

            discharge = PatientDischargeDetails(
                appointment=appointment,
                patientId=patient,
                doctorId=doctor,
                admitDate=admit_date,
                releaseDate=release_date,
                daySpent=day_spent,
                medicineCost=form.cleaned_data['medicineCost'],
                roomCharge=form.cleaned_data['roomCharge'],
                doctorFee=form.cleaned_data['doctorFee'],
                OtherCharge=form.cleaned_data['OtherCharge'],
                total=total
            )
            discharge.save()
            
            # Mark appointment as discharged
            appointment.is_discharged = True
            appointment.save()
            
            messages.success(request, f'Patient {patient.get_name} discharged from Dr. {doctor.get_name} successfully!')
            return redirect('admin-discharge')
    else:
        form = DischargeForm()
    
    return render(request, 'discharge_patient.html', {
        'appointment': appointment,
        'patient': patient,
        'doctor': doctor,
        'form': form
    })

@allowed_users(allowed_roles=['admin', 'patient'])
def download_invoice_view(request, pk):
    discharge = get_object_or_404(PatientDischargeDetails, id=pk)
    patient = discharge.patientId
    doctor = discharge.doctorId

    if request.user.is_authenticated and hasattr(request.user, 'patient'):
        if request.user.patient.id != patient.id:
            messages.error(request, 'You are not authorized to download this invoice.')
            return redirect('patient-dashboard')

    context = {
        'patient': patient,
        'doctor': doctor,
        'discharge': discharge,
        'hospital_name': 'City Hospital',
        'today': date.today(),
    }
    pdf = render_to_pdf('invoice_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Invoice_{patient.user.username}_{discharge.releaseDate}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("Not found")

# ---- DOCTOR VIEWS ----
@allowed_users(allowed_roles=['doctor'])
def doctor_dashboard_view(request):
    doctor = Doctor.objects.get(user=request.user)
    # Active appointments for this doctor (approved + not discharged)
    active_appointments = Appointment.objects.filter(
        doctorId=doctor,
        status=True,
        is_discharged=False
    )
    active_patients = Patient.objects.filter(appointment__in=active_appointments).distinct()
    
    # Discharged appointments for this doctor
    discharged_appointments = Appointment.objects.filter(
        doctorId=doctor,
        status=True,
        is_discharged=True
    )
    discharged_patients = Patient.objects.filter(appointment__in=discharged_appointments).distinct()
    
    context = {
        'patients': active_patients.count(),
        'discharged': discharged_patients.count(),
    }
    return render(request, 'doctor_dashboard.html', context)

@allowed_users(allowed_roles=['doctor'])
def doctor_patient_view(request):
    doctor = Doctor.objects.get(user=request.user)
    # Get all approved appointments for this doctor with patient details
    appointments = Appointment.objects.filter(
        doctorId=doctor,
        status=True
    ).select_related('patientId').order_by('-date')
    
    # Get discharged appointment IDs for this doctor
    discharged_appointment_ids = Appointment.objects.filter(
        doctorId=doctor,
        status=True,
        is_discharged=True
    ).values_list('id', flat=True)
    
    return render(request, 'doctor_patient.html', {
        'appointments': appointments,
        'discharged_appointment_ids': discharged_appointment_ids
    })

@allowed_users(allowed_roles=['doctor'])
def doctor_appointment_view(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctorId=doctor)
    return render(request, 'doctor_appointment.html', {'appointments': appointments})

@allowed_users(allowed_roles=['doctor'])
def delete_appointment_doctor_view(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.delete()
    messages.success(request, 'Appointment deleted!')
    return redirect('doctor-appointment')

# ---- PATIENT VIEWS ----
@allowed_users(allowed_roles=['patient'])
def patient_dashboard_view(request):
    patient = Patient.objects.get(user=request.user)
    doctor = patient.get_current_doctor
    discharge = PatientDischargeDetails.objects.filter(patientId=patient).first()
    
    context = {
        'patient': patient,
        'doctor': doctor,
        'discharge': discharge,
    }
    return render(request, 'patient_dashboard.html', context)

@allowed_users(allowed_roles=['patient'])
def patient_appointment_view(request):
    patient = Patient.objects.get(user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = Appointment(
                patientId=patient,
                doctorId=None,
                description=form.cleaned_data['description'],
                duration=form.cleaned_data['duration'],
                status=False,
                is_discharged=False
            )
            appointment.save()
            messages.success(request, 'Appointment requested. Admin will assign a doctor and approve.')
            return redirect('patient-appointment')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()

    appointments = Appointment.objects.filter(patientId=patient).order_by('-date')
    return render(request, 'patient_appointment.html', {
        'form': form,
        'appointments': appointments,
    })

@allowed_users(allowed_roles=['patient'])
def patient_doctor_view(request):
    patient = Patient.objects.get(user=request.user)
    doctor = patient.get_current_doctor
    return render(request, 'patient_doctor.html', {'doctor': doctor})

@allowed_users(allowed_roles=['patient'])
def patient_invoice_view(request):
    patient = Patient.objects.get(user=request.user)
    # Show all discharge records for this patient
    discharges = PatientDischargeDetails.objects.filter(patientId=patient)
    return render(request, 'patient_invoice.html', {
        'discharges': discharges,
        'patient': patient
    })