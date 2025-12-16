from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


class ModuleAccessMixin(LoginRequiredMixin):
    """Mixin to check module access for class-based views
    
    Usage:
        class MyView(ModuleAccessMixin, ListView):
            module_required = 'kitchen'
    """
    module_required = None
    
    def dispatch(self, request, *args, **kwargs):
        # Check authentication first
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusers always have access
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # Check module access if required
        if self.module_required:
            try:
                staff = request.user.staff_profile
                if not staff.has_module_access(self.module_required):
                    return HttpResponseForbidden(f'You do not have access to the {self.module_required} module.')
            except:
                return HttpResponseForbidden('You do not have staff access.')
        
        return super().dispatch(request, *args, **kwargs)
