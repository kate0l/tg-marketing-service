from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PartnerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['partner']


class UserRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['user', 'partner']