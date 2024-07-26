from django.shortcuts import redirect
from .models import Utilisateurs
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            try:
                request.user = Utilisateurs.objects.get(id=user_id)
            except Utilisateurs.DoesNotExist:
                request.user = None
        else:
            request.user = None

        response = self.get_response(request)
        return response

class ProtectUrls:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URL à protéger
        protected_urls = [
            reverse('adminPage'),
            
           
            # Ajoutez d'autres URL à protéger si nécessaire
        ]

        if any(url in request.path for url in protected_urls):
            if not request.session.get('user_id'):
                return redirect('login')

        response = self.get_response(request)
        return response