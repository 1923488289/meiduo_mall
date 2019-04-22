from django.shortcuts import render
from django.views.generic import View


class MyClass(View):
    def post(self, request):
        return render(request, 'register.html')

    def get(self, request):
        return render(request, 'register.html')
