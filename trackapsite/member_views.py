from django.shortcuts import render,redirect, HttpResponse
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from app.models import CustomUser
from django.utils.safestring import mark_safe
#from django.http import JsonResponse

@login_required(login_url='/')
def home(request):
    return render(request,'member/home.html')

def basic_information(request):
    return render(request,'member/basic_information.html')

