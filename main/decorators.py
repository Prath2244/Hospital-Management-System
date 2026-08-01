from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from .models import Doctor, Patient

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user = request.user
            group = None
            if user.is_superuser:
                group = 'admin'
            elif Doctor.objects.filter(user=user).exists():
                group = 'doctor'
            elif Patient.objects.filter(user=user).exists():
                group = 'patient'
            else:
                group = 'none'

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/')
        return wrapper_func
    return decorator