from django.shortcuts import redirect
from django.urls import reverse

class AdminRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect(reverse('not_authorized'))
        return self.get_response(request)