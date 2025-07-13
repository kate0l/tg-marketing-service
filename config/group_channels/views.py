from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.generic.base import View
# Create your views here.


class GroupProfileView(View):
    def get(self, request, *args, **kwargs):
        ...
        
        
class CreateGroupView(View):
    def get(self, request, *args, **kwargs):
        ...
        
        
class UpdateGruopView(View):
    def get(self, request, *args, **kwargs):
        ...
        
        
class DeleteGroupView(View):
    def get(self, request, *args, **kwargs):
        ...