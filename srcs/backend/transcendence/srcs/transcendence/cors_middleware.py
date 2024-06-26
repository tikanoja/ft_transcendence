from django.utils import timezone
from app.models import CustomUser
from django.contrib.auth import get_user_model

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "https://localhost, http://pong, https://c1r5p9"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-CSRFToken, Location, Transfer-Encoding"
        response["Access-Control-Expose-Headers"] = "Location"
        response["Access-Control-Allow-Credentials"] = "true"
        return response


class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        User = get_user_model()
        if request.user.is_authenticated:
            try:
                user = User.objects.get(username=request.user.username)
                user.last_seen = timezone.now()
                user.save()
            except User.DoesNotExist:
                return response
        return response


class NextParamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if response.status_code == 302 and 'Location' in response.headers:
            location = response.headers['Location']
            if location.endswith('/'):
                    location = location[:-1]
            while '?next=/app/' in location:
                location = location.replace('?next=/app/', '?next=/')
            while '/app' in location:
                location = location.replace('/app', '')
            if '/pong/post_pong_canvas' in location:
                location = location.replace('/pong/post_pong_canvas', '/play')
            response.headers['Location'] = location
            
        return response
