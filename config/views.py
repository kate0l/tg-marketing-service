from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View


def index(request):
    return render(
        request,
        'index.html'
    )