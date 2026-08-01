from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Doctor, Patient, Appointment, PatientDischargeDetails

class AdminSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

class DoctorSignupForm(UserCreationForm):
    mobile = forms.CharField(max_length=20)
    department = forms.ChoiceField(choices=[
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Emergency', 'Emergency'),
        ('Neurologist', 'Neurologist'),
        ('Pediatrician', 'Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
    ])
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'mobile', 'department', 'address']

class PatientSignupForm(UserCreationForm):
    mobile = forms.CharField(max_length=20)
    address = forms.CharField(widget=forms.Textarea)
    # REMOVED: symptoms field

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2', 'mobile', 'address']

class AppointmentForm(forms.ModelForm):
    duration = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 2 days, 1 week, 3 months'})
    )
    class Meta:
        model = Appointment
        fields = ['description', 'duration']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your symptoms...'}),
        }

class DischargeForm(forms.ModelForm):
    class Meta:
        model = PatientDischargeDetails
        fields = ['medicineCost', 'roomCharge', 'doctorFee', 'OtherCharge']
        widgets = {
            'medicineCost': forms.NumberInput(attrs={'class': 'form-control'}),
            'roomCharge': forms.NumberInput(attrs={'class': 'form-control'}),
            'doctorFee': forms.NumberInput(attrs={'class': 'form-control'}),
            'OtherCharge': forms.NumberInput(attrs={'class': 'form-control'}),
        }