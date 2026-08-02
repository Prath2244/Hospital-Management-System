from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),

    # Signups
    path('admin-signup/', views.admin_signup_view, name='admin-signup'),
    path('doctor-signup/', views.doctor_signup_view, name='doctor-signup'),
    path('patient-signup/', views.patient_signup_view, name='patient-signup'),

    # Logins
    path('admin-login/', views.admin_login_view, name='adminlogin'),
    path('doctor-login/', views.doctor_login_view, name='doctorlogin'),
    path('patient-login/', views.patient_login_view, name='patientlogin'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard_view, name='admin-dashboard'),
    path('admin-doctor/', views.admin_doctor_view, name='admin-doctor'),
    path('admin-pending-doctor/', views.admin_pending_doctor_view, name='admin-pending-doctor'),
    path('approve-doctor/<int:pk>/', views.approve_doctor_view, name='approve-doctor'),
    path('delete-doctor/<int:pk>/', views.delete_doctor_view, name='delete-doctor'),
    path('edit-doctor/<int:pk>/', views.edit_doctor_view, name='edit-doctor'),
    
    path('admin-patient/', views.admin_patient_view, name='admin-patient'),
    path('admin-unassigned-patient/', views.admin_unassigned_patient_view, name='admin-unassigned-patient'),
    path('approve-patient/<int:pk>/', views.approve_patient_view, name='approve-patient'),
    path('delete-patient/<int:pk>/', views.delete_patient_view, name='delete-patient'),
    path('assign-doctor/<int:pk>/', views.assign_doctor_view, name='assign-doctor'),
    
    path('admin-appointment/', views.admin_appointment_view, name='admin-appointment'),
    path('approve-appointment/<int:pk>/', views.approve_appointment_view, name='approve-appointment'),
    path('reject-appointment/<int:pk>/', views.reject_appointment_view, name='reject-appointment'),
    
    path('admin-discharge/', views.admin_discharge_view, name='admin-discharge'),
    path('discharge-patient/<int:pk>/', views.discharge_patient_view, name='discharge-patient'),
    path('download-invoice/<int:pk>/', views.download_invoice_view, name='download-invoice'),

    # Doctor
    path('doctor-dashboard/', views.doctor_dashboard_view, name='doctor-dashboard'),
    path('doctor-patient/', views.doctor_patient_view, name='doctor-patient'),
    path('doctor-appointment/', views.doctor_appointment_view, name='doctor-appointment'),
    path('delete-appointment-doctor/<int:pk>/', views.delete_appointment_doctor_view, name='delete-appointment-doctor'),

    # Patient
    path('patient-dashboard/', views.patient_dashboard_view, name='patient-dashboard'),
    path('patient-appointment/', views.patient_appointment_view, name='patient-appointment'),
    path('patient-doctor/', views.patient_doctor_view, name='patient-doctor'),
    path('patient-invoice/', views.patient_invoice_view, name='patient-invoice'),
]