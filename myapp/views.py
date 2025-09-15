from django.shortcuts import render, HttpResponse, redirect
from .models import financial_info
from .serializers import Financial_InfoSerializers
from rest_framework import viewsets
# render http pages

def home(request):
    pass

class Financial_InfoViewSet(viewsets.ModelViewSet):
     queryset= financial_info.objects.all()
     serializer_class = Financial_InfoSerializers

