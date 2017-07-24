from django.http import HttpResponse
from django.views.generic import View

class Test(View):
    def get(self, request, **kwargs):
        return HttpResponse(str(request.user) + '\n', content_type="text/plain")
