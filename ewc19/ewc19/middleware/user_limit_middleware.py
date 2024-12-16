from datetime import datetime
from django.contrib.sessions.models import Session
from django.shortcuts import render

class UserLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check the number of active user sessions
        active_sessions = Session.objects.filter(expire_date__gte=datetime.now()).count()
        if active_sessions >= 3:
            return render(request, 'maximum_user_limit.html')

        # Call the next middleware or view
        response = self.get_response(request)

        return response
