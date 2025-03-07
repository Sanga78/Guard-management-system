from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse('guard_dashboard'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def login_required_superuser_required(view_func):
    @login_required
    @superuser_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view
