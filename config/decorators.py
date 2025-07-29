from django.http import HttpResponseForbidden
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.role not in allowed_roles:
                return HttpResponseForbidden("Доступ запрещён")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def guest_required(view_func):
    return role_required(['guest'])(view_func)

def user_required(view_func):
    return role_required(['user', 'partner'])(view_func)

def partner_required(view_func):
    return role_required(['partner'])(view_func)